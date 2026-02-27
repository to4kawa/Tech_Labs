# Unit 11: Operations: 初動演習

> 60分設計（目安）: 目的5分 / 概念10分 / ハンズオン25分 / 検証10分 / 振り返り5分 / ミニ課題5分

## 0. 0円運用と安全上の注意
- 課金対象（VM/GKE/LBなど）は作成しない。
- GCP Free Tier + Cloud Shell + Colabのみで完結する。
- 攻撃/悪用の手順は扱わず、防御・監査・検知・運用のみを対象とする。
- APIキーや秘密情報はリポジトリへ保存しない（環境変数のみ）。

## 1. 目的（5分）
- 模擬インシデントを監査ログで時系列復元し、初動メモと封じ込め案を作成する。
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
### 4.1 模擬イベント発生（安全な管理操作）
```bash
export PROJECT_ID="$(gcloud config get-value project)"
gcloud projects get-iam-policy "${PROJECT_ID}" --format='none'
gcloud services list --enabled --limit=5
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.2 タイムライン抽出
```bash
gcloud logging read 'logName:"cloudaudit.googleapis.com%2Factivity" AND timestamp>="'"$(date -u -d '-30 min' +%Y-%m-%dT%H:%M:%SZ)"'"' --project="${PROJECT_ID}" --limit=20 --format='table(timestamp,protoPayload.serviceName,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail)'
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.3 初動メモ作成
```bash
cat > u11_initial_response.md <<'EOF'
## 初動メモ
- 事象検知時刻:
- 影響範囲:
- 直近操作:
- 一時封じ込め案:
EOF
cat u11_initial_response.md
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.4 封じ込め案と証跡
```bash
cat > u11_containment.md <<'EOF'
1) 不要なキー無効化
2) 高権限ロール棚卸し
3) 監査ログ保存期間確認
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.5 監査証跡パッケージ
```bash
mkdir -p u11_evidence
cp u11_initial_response.md u11_containment.md u11_evidence/
echo 'ログ出力と合わせて提出' > u11_evidence/README.txt
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
