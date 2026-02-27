# SecurityX実践コース（12ユニット）

このコースは、CompTIA SecurityX（旧CASP+相当）を4ドメインで実務化するための教材です。

## 学習ゴール
- セキュリティ判断を「根拠付き」で説明できる
- 手順を再現し、ログ証跡で妥当性を示せる
- 0円運用制約の中で、現場で使える設計・運用観点を身につける

## 現在の状況（最新）
- Unit-01〜Unit-12 の全ユニットを実装済み
- 各ユニットに `README.md` / `notebook.ipynb` / `quiz.md` / `rubric.md` を配置済み
- Unit-01 末尾の優先度順（02→10→04→08→11→05→07→03→09→06→12）に従って Unit-02〜12 を整備済み

## 構成
- シラバス: `syllabus.md`
- モジュール: `modules/unit-01` 〜 `modules/unit-12`
- テンプレート: `templates/`
- 補助資料: `tools/`

## まず最初に
1. `tools/setup/gcp_free_tier_guardrails.md` を読む
2. `modules/unit-01/README.md` を実施
3. `tools/checklists/evidence_checklist.md` で証跡の取り漏れを確認

## 最後の推奨
- 実施後は各ユニットの `notebook.ipynb` に証跡（コマンド結果/ログ抜粋/Explain-back）を必ず残す
- Unit-11（初動演習）→ Unit-12（事後レビュー）を連結して、月次で1回は復習する
