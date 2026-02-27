# Unit 01: クラウド実務の入口（最小権限IAM + Cloud Audit Logs）

> 60分で「最小権限」「意図的失敗」「監査ログで検証」「権限調整」を1ループ実施します。

## 0. 0円運用と安全上の注意
- **警告**: 課金対象リソース（VM、GKE、LB等）は作成しない。
- **回避策**: IAMとAudit Logsの閲覧のみを扱い、計算リソースを起動しない。
- **上限設定**: 予算アラートを必ず設定（`tools/setup/gcp_free_tier_guardrails.md`）。
- 本ユニットは防御・監査目的のみ。侵入/悪用手順は扱わない。

---

## 1. 目的（5分）
- IAM最小権限の考え方を実操作で理解する。
- 「権限不足による失敗」を監査ログで確認できるようにする。
- 調整後に成功ログを確認し、説明可能な証跡を残す。

## 2. 前提（5分）
- GCPプロジェクト1つ（学習用）
- Cloud Shell利用可能
- `gcloud auth login` 済み
- 課金アラート設定済み

## 3. 最小概念（10分）
- **最小権限（PoLP）**: 必要最小限のロールのみ付与。
- **失敗先行学習**: 意図的に不足権限で実行し、ログで原因を確認。
- **Cloud Audit Logs**:
  - Admin Activity: 管理操作（IAM変更など）
  - Data Access: データアクセス（サービスにより要設定）
- **検証軸**: `authorizationInfo.granted` の真偽。

## 4. 手順（25分）

### 4.1 変数を設定（コピペ可）
```bash
export PROJECT_ID="$(gcloud config get-value project)"
export STUDENT_USER="$(gcloud config get-value account)"
export LAB_SA_NAME="u01-lab-viewer"
export LAB_SA_EMAIL="${LAB_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "PROJECT_ID=${PROJECT_ID}"
echo "STUDENT_USER=${STUDENT_USER}"
```

期待出力例:
```text
PROJECT_ID=my-securityx-project
STUDENT_USER=learner@example.com
```

### 4.2 監査対象を作成（サービスアカウント）
```bash
gcloud iam service-accounts create "${LAB_SA_NAME}" \
  --display-name="SecurityX Unit01 Lab Viewer"
```

期待出力例:
```text
Created service account [u01-lab-viewer].
```

### 4.3 最小権限を付与（閲覧専用）
```bash
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${STUDENT_USER}" \
  --role="roles/iam.serviceAccountViewer"
```

### 4.4 意図的に失敗させる（作成/更新系を実行）
> Viewer権限では失敗する操作を実行して、失敗証跡を作る。

```bash
gcloud iam service-accounts update "${LAB_SA_EMAIL}" \
  --description="should-fail-at-first"
```

期待出力例（失敗）:
```text
PERMISSION_DENIED: Permission iam.serviceAccounts.update denied on resource
```

### 4.5 Cloud Audit Logsで失敗証跡を確認
```bash
gcloud logging read \
'resource.type="audited_resource" AND
 protoPayload.serviceName="iam.googleapis.com" AND
 protoPayload.methodName:"google.iam.admin.v1.UpdateServiceAccount"' \
--project="${PROJECT_ID}" \
--limit=5 \
--format='table(timestamp,protoPayload.authenticationInfo.principalEmail,protoPayload.authorizationInfo[0].granted,protoPayload.status.message)'
```

期待出力例:
```text
TIMESTAMP                    PRINCIPAL_EMAIL       GRANTED  STATUS_MESSAGE
2026-...                     learner@example.com   False    Permission iam.serviceAccounts.update denied...
```

### 4.6 必要最小限の追加権限を付与
```bash
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${STUDENT_USER}" \
  --role="roles/iam.serviceAccountAdmin"
```

### 4.7 再実行して成功させる
```bash
gcloud iam service-accounts update "${LAB_SA_EMAIL}" \
  --description="updated-after-minimum-adjustment"
```

期待出力例:
```text
Updated service account [u01-lab-viewer@...].
```

### 4.8 成功ログを確認（granted=true）
```bash
gcloud logging read \
'resource.type="audited_resource" AND
 protoPayload.serviceName="iam.googleapis.com" AND
 protoPayload.methodName:"google.iam.admin.v1.UpdateServiceAccount"' \
--project="${PROJECT_ID}" \
--limit=5 \
--format='table(timestamp,protoPayload.authenticationInfo.principalEmail,protoPayload.authorizationInfo[0].granted,protoPayload.status.message)'
```

期待出力例:
```text
TIMESTAMP                    PRINCIPAL_EMAIL       GRANTED  STATUS_MESSAGE
2026-...                     learner@example.com   True
```

### 4.9 後片付け（必須）
```bash
gcloud projects remove-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${STUDENT_USER}" \
  --role="roles/iam.serviceAccountAdmin"

gcloud projects remove-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${STUDENT_USER}" \
  --role="roles/iam.serviceAccountViewer"

gcloud iam service-accounts delete "${LAB_SA_EMAIL}" --quiet
```

---

## 5. 期待結果
- 失敗時ログで `granted=False` を確認できる。
- 権限調整後ログで `granted=True` を確認できる。
- 「なぜ失敗し、何を追加し、なぜ成功したか」を説明できる。

## 6. 失敗時対処
- `PROJECT_ID` が空: `gcloud config set project <PROJECT_ID>`
- ログが出ない: 1〜3分待って再実行
- `PERMISSION_DENIED` が継続: 付与ロールと対象メンバーを再確認
- 誤って高権限付与: 直ちに `remove-iam-policy-binding` で戻す

## 7. 検証（ログ/証跡）（10分）
- ログ種別: Cloud Audit Logs（IAM Admin Activity）
- 見る項目:
  - `protoPayload.authenticationInfo.principalEmail`
  - `protoPayload.authorizationInfo.granted`
  - `protoPayload.status.message`
- 証跡として残すもの:
  1. 失敗コマンドとエラー出力
  2. `granted=False` のログ出力
  3. 成功コマンド出力
  4. `granted=True` のログ出力

## 8. 振り返り（5分）

### 説明テンプレ（誰に何を説明するか）
- 説明相手A（チームリード）:
  - 「最小権限で開始したため更新操作は拒否。監査ログで拒否を確認後、必要最小限の権限追加で成功。」
- 説明相手B（監査担当）:
  - 「同一ユーザ・同一操作で `granted=False → True` へ遷移。変更理由と変更後の後片付けを実施済み。」
- 説明相手C（非技術マネージャ）:
  - 「失敗を先に確認することで、過剰権限の付与を避けながら必要作業を実現。」

## 9. ミニ課題（5分）
- 課題: `roles/iam.serviceAccountAdmin` の代わりに、さらに狭い権限組み合わせで同じ更新操作を成立させる案を調査し、根拠を1段落で記述。
- 提出物: 調査メモ（100〜200字）+ 参照URLまたは `gcloud iam roles describe` 出力抜粋。

## 10. クイズ（10問）
`quiz.md` を実施（回答・解説付き）。

## 11. 到達判定
`rubric.md` を参照。合格条件は以下:
- ハンズオン再現できる
- 証跡4点が揃っている
- クイズ 8/10 以上
- 説明テンプレで1分説明が成立

---

## Colabでの補助実行
- `notebook.ipynb` を開き、Cloud Shell結果の整理とExplain-backの下書きに使用。

## Unit-02以降の実装順（優先度）
1. Unit 02（GRC: ポリシー準拠チェック）
2. Unit 10（Operations: ログ基盤/検知）
3. Unit 04（Architecture: ゼロトラスト設計）
4. Unit 08（Engineering: 秘匿情報管理）
5. Unit 11（Operations: 初動演習）
6. Unit 05（Architecture: 設計レビュー）
7. Unit 07（Engineering: セキュアCI/CD）
8. Unit 03（GRC: リスク登録簿）
9. Unit 09（Engineering: IaCレビュー）
10. Unit 06（Architecture: 可用性設計）
11. Unit 12（Operations: 事後レビュー）
