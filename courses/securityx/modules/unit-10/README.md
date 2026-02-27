# Unit 10: Operations: ログ基盤/検知

> 60分設計（目安）: 目的5分 / 概念10分 / ハンズオン25分 / 検証10分 / 振り返り5分 / ミニ課題5分

## 0. 0円運用と安全上の注意
- 課金対象（VM/GKE/LBなど）は作成しない。
- GCP Free Tier + Cloud Shell + Colabのみで完結する。
- 攻撃/悪用の手順は扱わず、防御・監査・検知・運用のみを対象とする。
- APIキーや秘密情報はリポジトリへ保存しない（環境変数のみ）。

## 1. 目的（5分）
- Loggingの集約とフィルタ、ログベースメトリクス、アラート作成までを無料範囲で体験する。
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
### 4.1 変数設定
```bash
export PROJECT_ID="$(gcloud config get-value project)"
export METRIC_NAME="u10_iam_policy_change"
export ALERT_NAME="u10-iam-policy-alert
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.2 検知対象イベントを発生
```bash
gcloud projects get-iam-policy "${PROJECT_ID}" --format='none'
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.3 フィルタでイベント確認
```bash
gcloud logging read 'logName:"cloudaudit.googleapis.com%2Factivity" AND protoPayload.serviceName="cloudresourcemanager.googleapis.com"' --project="${PROJECT_ID}" --limit=5 --format='table(timestamp,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail)'
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.4 ログベースメトリクス作成
```bash
gcloud logging metrics create "${METRIC_NAME}"   --description="IAM policy change detector"   --log-filter='protoPayload.methodName="SetIamPolicy"'
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.5 アラートポリシーを作成
```bash
cat > u10_alert.json <<'EOF'
{
  "displayName": "u10-iam-policy-alert",
  "conditions": [{"displayName":"policy change","conditionThreshold":{"filter":"metric.type="logging.googleapis.com/user/u10_iam_policy_change" resource.type="global"","comparison":"COMPARISON_GT","thresholdValue":0,"duration":"0s","trigger":{"count":1}}}],
  "combiner": "OR",
  "enabled": true
}
EOF
gcloud alpha monitoring policies create --policy-from-file=u10_alert.json
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.6 後片付け
```bash
gcloud alpha monitoring policies list --format='value(name,displayName)' | grep "${ALERT_NAME}" | awk '{print $1}' | xargs -r gcloud alpha monitoring policies delete --quiet
gcloud logging metrics delete "${METRIC_NAME}" --quiet
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
