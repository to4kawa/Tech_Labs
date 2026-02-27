# Unit 05: Architecture: 設計レビュー

> 60分設計（目安）: 目的5分 / 概念10分 / ハンズオン25分 / 検証10分 / 振り返り5分 / ミニ課題5分

## 0. 0円運用と安全上の注意
- 課金対象（VM/GKE/LBなど）は作成しない。
- GCP Free Tier + Cloud Shell + Colabのみで完結する。
- 攻撃/悪用の手順は扱わず、防御・監査・検知・運用のみを対象とする。
- APIキーや秘密情報はリポジトリへ保存しない（環境変数のみ）。

## 1. 目的（5分）
- レビュー観点表を使って設計案を評価し、指摘と改善策を提示する。
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
### 4.1 観点表を作成
```bash
cat > u05_review_checklist.csv <<'EOF'
観点,確認項目,判定,根拠
可用性,単一障害点がないか,NG,単一リージョン
最小権限,IAMが職務分離されているか,OK,viewer中心
監査,操作ログが追跡可能か,OK,Audit Logs
鍵管理,秘密が平文でないか,NG,環境変数未整理
境界,公開アクセスが制限されているか,OK,allUsersなし
EOF
column -s, -t u05_review_checklist.csv
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.2 対象設計のレビュー
```bash
cat > u05_design_notes.md <<'EOF'
- 既存案: Cloud Run + Firestore + Pub/Sub
- 指摘: DR未定義、秘密管理ルール不足
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.3 改善案作成
```bash
cat > u05_fix_plan.md <<'EOF'
- バックアップ/復旧手順を追加
- Secret運用標準を追加
- 四半期ごとにIAMレビュー
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.4 ログで運用可能性確認
```bash
gcloud logging read 'protoPayload.serviceName="run.googleapis.com" OR protoPayload.serviceName="iam.googleapis.com"' --limit=5 --format='table(timestamp,protoPayload.serviceName,protoPayload.methodName)'
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.5 提出物整理
```bash
mkdir -p u05_artifacts
cp u05_review_checklist.csv u05_design_notes.md u05_fix_plan.md u05_artifacts/
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
