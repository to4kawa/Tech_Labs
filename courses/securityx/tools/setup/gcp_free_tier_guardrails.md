# GCP Free Tier Guardrails（0円運用ガードレール）

## 1) 事前設定（必須）
1. Cloud Billing で予算アラートを作成（例: 100 JPY/月）
2. 通知先メールを設定
3. 不要プロジェクトは削除

## 2) 原則
- 常時稼働リソース（VM、GKEクラスター、外部LB）を作らない
- 演習後に作成物を削除
- 無料枠対象外機能は使わない

## 3) 課金リスクがある操作の扱い
- 手順に必ず「警告」「回避策」「上限設定」を記載
- 不明な場合は実行しない

## 4) 演習前チェック（Cloud Shell）
```bash
gcloud config list project
gcloud services list --enabled | head
```

## 5) 演習後チェック
```bash
gcloud projects get-iam-policy "$GOOGLE_CLOUD_PROJECT" --format='table(bindings.role)'
```
