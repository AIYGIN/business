#!/usr/bin/env python3
"""Create a proposal draft Markdown file in the user's home directory."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:48] or "draft"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create proposal draft markdown in home directory")
    parser.add_argument("theme", nargs="?", default="draft", help="Proposal theme")
    parser.add_argument("--slug", default=None, help="Optional ASCII slug for filename")
    args = parser.parse_args()

    now = datetime.now().strftime("%Y%m%d_%H%M")
    slug = slugify(args.slug or args.theme)
    path = Path.home() / f"proposal_{slug}_{now}.md"

    content = f"""# 提案書ドラフト: {args.theme}

## 0. 人間レビュー用サマリー
- 結論: 
- 意思決定してほしいこと: 
- 最重要確認ポイント: 

## 1. SCQA骨格
### S: 現状

### C: 課題

### Q: 問い

### A: 提案

## 2. 提案本文たたき台
### 2.1 結論

### 2.2 背景

### 2.3 課題

### 2.4 提案内容

### 2.5 実行ステップ

### 2.6 期待効果

### 2.7 コスト・体制・期限

## 3. 数字・根拠の確認リスト
| 記述 | 必要な出典 | 現状 | 確認担当 |
|---|---|---|---|

## 4. 決裁者からの想定質問
| 質問 | 回答案 | 追加で必要な情報 |
|---|---|---|

## 5. 弱点と改善案
- 最も弱いセクション:
- 理由:
- この1点だけ直すなら:

## 6. 人間レビュー欄
- [ ] 事実関係を確認した
- [ ] 数字の出典を確認した
- [ ] 決裁者の関心に合っている
- [ ] 実行責任者が明確
- [ ] 期限・費用・リスクが明確
- [ ] 最終提出前に人間が文章を読み直した

## 7. AI作業メモ
- 仮定:
- 未確認事項:
- 次に人間が直すべき箇所:
"""
    path.write_text(content, encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
