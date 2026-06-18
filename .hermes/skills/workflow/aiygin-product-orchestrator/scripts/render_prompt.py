#!/usr/bin/env python3
"""AIYGIN product orchestration prompt renderer.

This script renders phase-specific Codex prompts for Hermes-driven FE/BFF
orchestration. It intentionally does not create issues, edit code, or run Codex
unless a human/agent explicitly passes the rendered prompt to Codex.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PHASES = {
    "bff-issue-draft": "references/bff-issue-draft-prompt.md",
    "bff-issue-create": "references/bff-issue-create-prompt.md",
    "bff-mock-pr": "references/bff-mock-pr-prompt.md",
    "fe-issue-draft": "references/fe-issue-draft-prompt.md",
    "fe-issue-create": "references/fe-issue-create-prompt.md",
    "fe-dev-pr": "references/fe-dev-pr-prompt.md",
}


def read_optional(path: str | None) -> str:
    if not path:
        return "未指定"
    return Path(path).expanduser().read_text(encoding="utf-8")


def replace_all(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value or "未指定")
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description="Render AIYGIN Codex phase prompt")
    parser.add_argument("--phase", required=True, choices=sorted(PHASES))
    parser.add_argument("--business-url", default="未指定")
    parser.add_argument("--bff-issue-url", default="未指定")
    parser.add_argument("--bff-mock-pr-url", default="未指定")
    parser.add_argument("--fe-issue-url", default="未指定")
    parser.add_argument("--issue-title", default="未指定")
    parser.add_argument("--issue-body", default="未指定")
    parser.add_argument("--issue-body-file", help="Approved issue body markdown file")
    parser.add_argument("--delegation-input", default="未指定")
    parser.add_argument("--input-file", help="Delegation input markdown file")
    parser.add_argument("--bff-openapi-summary", default="未指定")
    parser.add_argument("--bff-openapi-summary-file")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    template = (skill_dir / PHASES[args.phase]).read_text(encoding="utf-8")

    values = {
        "BUSINESS_ISSUE_URL": args.business_url,
        "BFF_ISSUE_URL": args.bff_issue_url,
        "BFF_MOCK_PR_URL": args.bff_mock_pr_url,
        "FE_ISSUE_URL": args.fe_issue_url,
        "ISSUE_TITLE": args.issue_title,
        "ISSUE_BODY": read_optional(args.issue_body_file) if args.issue_body_file else args.issue_body,
        "DELEGATION_INPUT": read_optional(args.input_file) if args.input_file else args.delegation_input,
        "BFF_OPENAPI_SUMMARY": read_optional(args.bff_openapi_summary_file)
        if args.bff_openapi_summary_file
        else args.bff_openapi_summary,
    }

    print(replace_all(template, values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
