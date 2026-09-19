# CLAUDE.md — Kaggriculture エージェント開発

**返答はすべて日本語で書く。**

作業ルールの正は `AGENTS.md`（Claude Code / Codex 共通）。下の行で読み込む。
ルールを変えるときは `AGENTS.md` を直し、このファイルには Claude Code 固有のことだけを書く。

@AGENTS.md

## Claude Code 固有

- Claude の提出コマンド実行は自動モードの分類器で止められる。回避しようとせず、コマンドをユーザーに渡す（AGENTS.md §0）。
- 一時ファイル・分析スクリプトはセッションの scratchpad に置き、リポジトリに残すものだけを `scripts\` に置く。
