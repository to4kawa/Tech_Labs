# Unit 03: GRC: リスク登録簿

> 60分設計（目安）: 目的5分 / 概念10分 / ハンズオン25分 / 検証10分 / 振り返り5分 / ミニ課題5分

## 0. 0円運用と安全上の注意
- 課金対象（VM/GKE/LBなど）は作成しない。
- GCP Free Tier + Cloud Shell + Colabのみで完結する。
- 攻撃/悪用の手順は扱わず、防御・監査・検知・運用のみを対象とする。
- APIキーや秘密情報はリポジトリへ保存しない（環境変数のみ）。

## 1. 目的（5分）
- リスク登録簿を作成し、優先度とコントロール、検証方法をつなげる。
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
### 4.1 テンプレート作成
```bash
cat > u03_risk_register.csv <<'EOF'
ID,リスク,可能性,影響,優先度,コントロール,検証手段
R-01,過剰IAM権限,中,高,高,四半期棚卸し,Audit Logs
R-02,公開設定ミス,中,高,高,公開禁止ポリシー,Policy/IAM差分
R-03,秘密漏えい,低,高,中,.gitignore+scan,スキャンログ
EOF
column -s, -t u03_risk_register.csv
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.2 優先度計算補助
```bash
python - <<'EOF'
import csv
m={'低':1,'中':2,'高':3}
with open('u03_risk_register.csv') as f:
    r=list(csv.DictReader(f))
for x in r:
    print(x['ID'], m[x['可能性']]*m[x['影響']])
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.3 対応計画
```bash
cat > u03_treatment_plan.md <<'EOF'
- R-01: IAM Viewer基準線を定義
- R-02: allUsers検知を日次化
- R-03: PR時シークレット検査
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.4 ログ検証クエリ準備
```bash
cat > u03_log_queries.txt <<'EOF'
protoPayload.methodName="SetIamPolicy"
protoPayload.serviceName="iam.googleapis.com"
EOF
cat u03_log_queries.txt
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.5 証跡化
```bash
mkdir -p u03_evidence
cp u03_risk_register.csv u03_treatment_plan.md u03_log_queries.txt u03_evidence/
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
