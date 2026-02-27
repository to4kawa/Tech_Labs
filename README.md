# Tech Labs: SecurityX (CASP+相当) 実践教材

このリポジトリは、**CISSP保有だが実務経験が薄い学習者**向けに、CompTIA SecurityX（旧CASP+相当）の4ドメインを60分単位で反復学習できるように設計した教材です。

- 対象: GRC / Architecture / Engineering / Operations
- 構成: 全12ユニット（各ドメイン3ユニット）
- 進め方: 理屈 → 手順 → 証跡 → 言語化 → 小テスト
- 実行基盤: **GCP Free Tier + Cloud Shell + Google Colab（原則0円）**

---

## 学習の回し方（1ユニット60分）

1. **目的/前提（5分）**
2. **最小概念（10分）**
3. **ハンズオン（25分）**
4. **検証（ログ/証跡）（10分）**
5. **振り返り（5分）**
6. **ミニ課題（5分）**

到達判定:
- 説明テンプレで要点を言語化できる
- ハンズオンを再現できる
- クイズで **8/10以上**

---

## 0円運用ポリシー

- 課金対象リソースは作成しない（VM/外部IP常時利用/有償APIなどを回避）。
- 使うサービスは無料利用枠・ログ閲覧中心。
- 手順内で課金リスクがある場合は、必ず以下3点を記載:
  1) 警告
  2) 回避策
  3) 上限設定方法（Budget/アラート/削除手順）
- 作業前に `courses/securityx/tools/setup/gcp_free_tier_guardrails.md` を確認。

---

## 安全ポリシー

- 本教材は**防御・検知・ログ検証**に限定。
- 侵入・悪用を目的とする具体的手順は扱わない。
- Secrets（APIキー、サービスアカウント秘密鍵等）をリポジトリに保存しない。
- 機密情報は環境変数または対話入力で扱う。

---

## ユニット導線

- コース入口: `courses/securityx/README.md`
- 全体シラバス: `courses/securityx/syllabus.md`
- Unit 01（完全実装）: `courses/securityx/modules/unit-01/README.md`
- Unit 02〜12（雛形）: `courses/securityx/modules/unit-0X/README.md`
- 再利用テンプレート:
  - `courses/securityx/templates/unit-template.md`
  - `courses/securityx/templates/incident-notes-template.md`
  - `courses/securityx/templates/architecture-review-template.md`

---

## 次にやること（推奨）

1. Unit 01 を実施して学習ループを体験
2. Unit 02 以降を優先順に拡張（優先順は Unit 01 README末尾参照）
3. 学習ログをテンプレートで蓄積して説明力を強化
