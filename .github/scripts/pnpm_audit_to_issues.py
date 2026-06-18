#!/usr/bin/env python3
"""Create/update AIYGIN/business issues from pnpm audit JSON reports.

The workflow intentionally keeps GitHub Actions responsible only for detection
and issue creation. Hermes/Codex remediation is handled by a separate loop that
watches these issues.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_LABELS = ["security", "pnpm-audit", "agent:todo"]
SEVERITY_ORDER = {"critical": 4, "high": 3, "moderate": 2, "medium": 2, "low": 1, "info": 0, "unknown": 0}


@dataclass(frozen=True)
class ReportSpec:
    key: str
    repo: str
    path: Path


@dataclass
class Finding:
    repo_key: str
    repo: str
    package: str
    severity: str
    title: str
    advisory_id: str
    url: str
    vulnerable_versions: str
    patched_versions: str
    recommendation: str
    paths: list[str]
    raw: dict[str, Any]

    @property
    def stable_id(self) -> str:
        src = "|".join([self.repo, self.package, self.advisory_id or self.title, self.severity])
        return hashlib.sha1(src.encode("utf-8")).hexdigest()[:12]

    @property
    def title_for_issue(self) -> str:
        title = self.title or self.advisory_id or "pnpm audit vulnerability"
        return f"[Security][pnpm audit][{self.repo_key}] {self.package}: {title}"

    @property
    def labels(self) -> list[str]:
        labels = [*DEFAULT_LABELS, f"repo:{self.repo_key}"]
        if self.severity in {"critical", "high", "moderate", "medium", "low"}:
            labels.append(f"severity:{'moderate' if self.severity == 'medium' else self.severity}")
        return labels


def run(cmd: list[str], *, check: bool = True) -> str:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc.stdout.strip()


def normalize_severity(value: Any) -> str:
    sev = str(value or "unknown").lower()
    return "moderate" if sev == "medium" else sev


def parse_report_spec(value: str) -> ReportSpec:
    # Format: key=owner/repo:path/to/audit.json
    if "=" not in value or ":" not in value:
        raise argparse.ArgumentTypeError("--report must be key=owner/repo:path/to/audit.json")
    key, rest = value.split("=", 1)
    repo, path = rest.split(":", 1)
    return ReportSpec(key=key, repo=repo, path=Path(path))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc


def findings_from_advisories(spec: ReportSpec, data: dict[str, Any]) -> list[Finding]:
    advisories = data.get("advisories") or {}
    findings: list[Finding] = []
    if isinstance(advisories, dict):
        iterable = advisories.values()
    elif isinstance(advisories, list):
        iterable = advisories
    else:
        iterable = []

    for adv in iterable:
        if not isinstance(adv, dict):
            continue
        module_name = str(adv.get("module_name") or adv.get("name") or adv.get("package") or "unknown-package")
        finding = Finding(
            repo_key=spec.key,
            repo=spec.repo,
            package=module_name,
            severity=normalize_severity(adv.get("severity")),
            title=str(adv.get("title") or adv.get("overview") or "pnpm audit vulnerability"),
            advisory_id=str(adv.get("github_advisory_id") or adv.get("cves") or adv.get("id") or ""),
            url=str(adv.get("url") or adv.get("recommendation_url") or ""),
            vulnerable_versions=str(adv.get("vulnerable_versions") or adv.get("range") or ""),
            patched_versions=str(adv.get("patched_versions") or ""),
            recommendation=str(adv.get("recommendation") or "pnpm update / dependency upgrade を検討してください。"),
            paths=[str(p) for p in adv.get("findings", [])] if isinstance(adv.get("findings"), list) else [],
            raw=adv,
        )
        findings.append(finding)
    return findings


def flatten_via(via: Any) -> tuple[list[str], list[dict[str, Any]]]:
    names: list[str] = []
    objects: list[dict[str, Any]] = []
    if not isinstance(via, list):
        return names, objects
    for item in via:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            objects.append(item)
            if item.get("title"):
                names.append(str(item["title"]))
            elif item.get("source"):
                names.append(str(item["source"]))
    return names, objects


def findings_from_vulnerabilities(spec: ReportSpec, data: dict[str, Any]) -> list[Finding]:
    vulnerabilities = data.get("vulnerabilities") or {}
    findings: list[Finding] = []
    if not isinstance(vulnerabilities, dict):
        return findings

    for package, vuln in vulnerabilities.items():
        if not isinstance(vuln, dict):
            continue
        via_names, via_objects = flatten_via(vuln.get("via"))
        base = via_objects[0] if via_objects else {}
        title = str(base.get("title") or ", ".join(via_names) or "pnpm audit vulnerability")
        advisory_id = str(base.get("source") or base.get("url") or title)
        finding = Finding(
            repo_key=spec.key,
            repo=spec.repo,
            package=str(package),
            severity=normalize_severity(vuln.get("severity") or base.get("severity")),
            title=title,
            advisory_id=advisory_id,
            url=str(base.get("url") or ""),
            vulnerable_versions=str(base.get("range") or vuln.get("range") or ""),
            patched_versions=str(base.get("fixAvailable") or vuln.get("fixAvailable") or ""),
            recommendation="pnpm audit の fixAvailable / patched range を確認し、直接依存または override 更新で解消してください。",
            paths=[str(n) for n in vuln.get("nodes", [])] if isinstance(vuln.get("nodes"), list) else [],
            raw=vuln,
        )
        findings.append(finding)
    return findings


def extract_findings(spec: ReportSpec) -> list[Finding]:
    data = load_json(spec.path)
    findings = findings_from_advisories(spec, data) or findings_from_vulnerabilities(spec, data)
    findings.sort(key=lambda f: (-SEVERITY_ORDER.get(f.severity, 0), f.package, f.title))
    return findings


def issue_body(finding: Finding) -> str:
    raw = json.dumps(finding.raw, ensure_ascii=False, indent=2, sort_keys=True)
    paths = "\n".join(f"- `{p}`" for p in finding.paths[:20]) or "- 未取得"
    return f"""## 概要

`pnpm audit --json` により `{finding.repo}` で脆弱性が検出されました。

## 対象

- repository: `{finding.repo}`
- audit source: `{finding.repo_key}`
- package: `{finding.package}`
- severity: `{finding.severity}`
- advisory: `{finding.advisory_id or '未取得'}`
- URL: {finding.url or '未取得'}

## 影響範囲

- vulnerable versions: `{finding.vulnerable_versions or '未取得'}`
- patched versions / fixAvailable: `{finding.patched_versions or '未取得'}`

## pnpm audit の検出 path

{paths}

## 推奨対応

- [ ] 対象 repository の `pnpm-lock.yaml` と直接依存を確認する。
- [ ] 直接依存の更新、transitive dependency の解消、または `pnpm.overrides` を検討する。
- [ ] 変更後に `pnpm audit --json` で該当 advisory が消えることを確認する。
- [ ] 変更後に repository の標準 check / test を実行する。
- [ ] 修正 PR を作成し、この Issue にリンクする。

## Hermes/Codex 対応メモ

- stable id: `{finding.stable_id}`
- Hermes cron は `pnpm-audit` / `agent:todo` label の open Issue を捕捉し、対象 repository の Codex へ修正指示する。
- 自動 merge はしない。PR は人間レビュー前提にする。

## raw audit item

<details>
<summary>JSON</summary>

```json
{raw}
```

</details>
"""


def ensure_label(repo: str, label: str) -> None:
    color = {
        "security": "D73A4A",
        "pnpm-audit": "B60205",
        "agent:todo": "FBCA04",
    }.get(label, "C2E0C6")
    run(["gh", "label", "create", label, "--repo", repo, "--color", color, "--force"], check=False)


def get_open_audit_issues(repo: str) -> dict[str, dict[str, Any]]:
    out = run([
        "gh", "issue", "list", "--repo", repo, "--state", "open", "--label", "pnpm-audit",
        "--limit", "200", "--json", "number,title,url",
    ])
    items = json.loads(out or "[]")
    return {item["title"]: item for item in items}


def create_or_update_issue(
    business_repo: str,
    finding: Finding,
    existing: dict[str, dict[str, Any]],
    *,
    dry_run: bool = False,
) -> str:
    title = finding.title_for_issue
    if dry_run:
        action = "update" if title in existing else "create"
        print(json.dumps({
            "action": action,
            "repo": business_repo,
            "title": title,
            "labels": finding.labels,
            "stable_id": finding.stable_id,
        }, ensure_ascii=False))
        return f"dry-run:{action}:{finding.stable_id}"

    for label in finding.labels:
        ensure_label(business_repo, label)
    body_path = Path(f"/tmp/pnpm-audit-{finding.stable_id}.md")
    body_path.write_text(issue_body(finding), encoding="utf-8")

    if title in existing:
        issue = existing[title]
        run(["gh", "issue", "comment", str(issue["number"]), "--repo", business_repo, "--body-file", str(body_path)])
        print(f"updated {issue['url']}")
        return issue["url"]

    args = ["gh", "issue", "create", "--repo", business_repo, "--title", title, "--body-file", str(body_path)]
    for label in finding.labels:
        args.extend(["--label", label])
    url = run(args)
    print(f"created {url}")
    return url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--business-repo", default="AIYGIN/business")
    parser.add_argument("--report", action="append", type=parse_report_spec, required=True)
    parser.add_argument("--dry-run", action="store_true", help="Parse reports and print planned issue operations without calling gh")
    args = parser.parse_args()

    existing = {} if args.dry_run else get_open_audit_issues(args.business_repo)
    total = 0
    for spec in args.report:
        findings = extract_findings(spec)
        if not findings:
            print(f"no vulnerabilities: {spec.key} ({spec.repo})")
            continue
        for finding in findings:
            create_or_update_issue(args.business_repo, finding, existing, dry_run=args.dry_run)
            total += 1
    print(f"processed findings: {total}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # GitHub Actions should fail loudly on parser/API errors.
        print(f"error: {exc}", file=sys.stderr)
        raise
