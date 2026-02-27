# Unit 07: Engineering: セキュアCI/CD

> 60分設計（目安）: 目的5分 / 概念10分 / ハンズオン25分 / 検証10分 / 振り返り5分 / ミニ課題5分

## 0. 0円運用と安全上の注意
- 課金対象（VM/GKE/LBなど）は作成しない。
- GCP Free Tier + Cloud Shell + Colabのみで完結する。
- 攻撃/悪用の手順は扱わず、防御・監査・検知・運用のみを対象とする。
- APIキーや秘密情報はリポジトリへ保存しない（環境変数のみ）。

## 1. 目的（5分）
- Secrets禁止・依存関係検査・静的解析・レビューゲートの最小構成を再現する。
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
### 4.1 CIポリシーファイル作成
```bash
mkdir -p .github/workflows
cat > .github/workflows/u07-secure-ci.yml <<'EOF'
name: u07-secure-ci
on: [pull_request]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: "! git grep -nE '(API_KEY|SECRET|TOKEN)'"
      - run: "python -m pip install pip-audit && pip-audit || true"
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.2 ローカル疑似実行
```bash
git grep -nE '(API_KEY|SECRET|TOKEN)' || echo 'no hardcoded secrets'
python -m pip install --user pip-audit >/dev/null 2>&1 || true
python -m pip_audit --version || true
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.3 レビューゲート定義
```bash
cat > u07_review_gate.md <<'EOF'
- PR必須
- CODEOWNERSレビュー1名以上
- CI成功までマージ禁止
EOF
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.4 署名/来歴確認の考え方
```bash
git log --oneline -n 5
```
期待結果例: コマンドが正常終了し、指定ファイルまたはログが確認できる。

### 4.5 証跡
```bash
mkdir -p u07_evidence
cp .github/workflows/u07-secure-ci.yml u07_review_gate.md u07_evidence/
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
