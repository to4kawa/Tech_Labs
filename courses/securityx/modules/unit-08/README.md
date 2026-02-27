# Unit 08: Engineering: 秘匿情報管理

> 60分設計（目安）: 目的5分 / 概念10分 / ハンズオン25分 / 検証10分 / 振り返り5分 / ミニ課題5分

## 0. 0円運用と安全上の注意
- 課金対象（VM/GKE/LBなど）は作成しない。
- GCP Free Tier + Cloud Shell + Colabのみで完結する。
- 攻撃/悪用の手順は扱わず、防御・監査・検知・運用のみを対象とする。
- APIキーや秘密情報はリポジトリへ保存しない（環境変数のみ）。

## 1. 目的（5分）
- 秘密情報をリポジトリへ保存しない運用を確立し、漏えい検知の基本を実践する。
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
### 4.1 環境変数で秘密を扱う
```bash
read -s -p 'API token: ' LAB_TOKEN; echo
export LAB_TOKEN
python - <<'EOF'
import os
print('token loaded:', bool(os.getenv('LAB_TOKEN')))
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.2 .gitignore確認
```bash
printf '
.env
secrets/*.txt
' >> .gitignore
tail -n 5 .gitignore
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.3 漏えいスキャン（ローカル）
```bash
cat > u08_fake_leak.txt <<'EOF'
DUMMY_KEY=ABCD1234-DO-NOT-USE
EOF
rg -n '(KEY|TOKEN|SECRET)' .
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.4 修正と再スキャン
```bash
rm -f u08_fake_leak.txt
rg -n '(ABCD1234-DO-NOT-USE)' . || echo 'no leak pattern found'
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.5 監査ログ確認
```bash
gcloud logging read 'protoPayload.serviceName="secretmanager.googleapis.com" OR protoPayload.serviceName="iam.googleapis.com"' --limit=5 --format='table(timestamp,protoPayload.serviceName,protoPayload.methodName)'
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
