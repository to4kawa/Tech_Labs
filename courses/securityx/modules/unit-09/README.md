# Unit 09: Engineering: IaCレビュー

> 60分設計（目安）: 目的5分 / 概念10分 / ハンズオン25分 / 検証10分 / 振り返り5分 / ミニ課題5分

## 0. 0円運用と安全上の注意
- 課金対象（VM/GKE/LBなど）は作成しない。
- GCP Free Tier + Cloud Shell + Colabのみで完結する。
- 攻撃/悪用の手順は扱わず、防御・監査・検知・運用のみを対象とする。
- APIキーや秘密情報はリポジトリへ保存しない（環境変数のみ）。

## 1. 目的（5分）
- IaCコードの危険設定をレビューし、修正案を示してデプロイ前品質を高める。
- 実行結果をログ/証跡で説明できる状態になる。

## 2. 前提（5分）
- 学習用GCPプロジェクト
- Cloud Shellで`gcloud auth login`済み
- `jq`/`python`が利用可能
- 予算アラート設定済み

## 3. 最小概念（10分）
- 最小権限（PoLP）
- 変更前後の差分確認
- Cloud Audit Logs/Cloud Loggingでの証跡確認
- 失敗→修正→再検証の反復

## 4. 手順（25分）
### 4.1 サンプルIaC作成
```bash
cat > u09_main.tf <<'EOF'
resource "google_storage_bucket" "bad" {
  name          = "replace-me-u09"
  location      = "ASIA"
  force_destroy = true
  uniform_bucket_level_access = false
}
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.2 レビュー観点で検出
```bash
cat > u09_review.md <<'EOF'
- force_destroy=true は誤削除リスク
- UBLA=false は権限管理複雑化
- name未管理は衝突リスク
EOF
cat u09_review.md
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.3 修正案作成
```bash
cat > u09_main_fixed.tf <<'EOF'
resource "google_storage_bucket" "good" {
  name          = "replace-me-u09-fixed"
  location      = "ASIA"
  force_destroy = false
  uniform_bucket_level_access = true
  public_access_prevention = "enforced"
}
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.4 静的確認（デプロイ不要）
```bash
diff -u u09_main.tf u09_main_fixed.tf || true
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.5 証跡整理
```bash
mkdir -p u09_evidence
cp u09_main.tf u09_main_fixed.tf u09_review.md u09_evidence/
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

## 5. 期待結果
- 手順実行により、対象テーマの設定/文書/ログが揃う。
- 少なくとも1つの操作について監査ログまたは設定差分で検証できる。

## 6. 失敗時対処
- `PROJECT_ID`が空: `gcloud config set project <PROJECT_ID>`
- ログ反映が遅い: 2〜5分待って再試行
- 権限不足: 現在アカウントと必要ロールを確認
- 不要な設定を作った: 後片付け手順で削除

## 7. 検証（ログ/証跡）（10分）
- 確認ログ: Cloud Audit Logs / Cloud Logging
- 確認項目: 実行主体、メソッド名、成否、設定差分
- 提出証跡（最低4点）:
  1. 実行コマンド
  2. 実行結果（成功/失敗）
  3. ログ抽出結果
  4. 修正後の再検証結果

## 8. 振り返り（5分）
- Explain-backテンプレ:
  - 何を目的に実施したか
  - どのログで何を検証したか
  - 次回改善する点

## 9. 10問クイズ
- `quiz.md`を実施（解答・解説付き）。

## 10. ミニ課題（5分）
- 本ユニットの手順を自チーム向けに1つ短縮し、再現性を維持した改善版手順を100〜200字で作成する。

## 11. 到達判定
- `rubric.md`を参照。説明テンプレで言語化 + ハンズオン再現 + クイズ8/10以上を満たすこと。

## Colabメモ
- `notebook.ipynb`に、Cloud Shell実行結果、証跡リンク、Explain-back下書きを記録する。
