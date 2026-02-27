#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
METHOD='google.iam.admin.v1.UpdateServiceAccount'

if [[ -z "${PROJECT_ID}" ]]; then
  echo "[ERROR] PROJECT_ID is empty. Pass as first arg or set gcloud project." >&2
  exit 1
fi

echo "[INFO] Reading IAM update audit logs from project: ${PROJECT_ID}"
gcloud logging read \
"resource.type=\"audited_resource\" AND protoPayload.serviceName=\"iam.googleapis.com\" AND protoPayload.methodName:\"${METHOD}\"" \
  --project="${PROJECT_ID}" \
  --limit=10 \
  --format='table(timestamp,protoPayload.authenticationInfo.principalEmail,protoPayload.authorizationInfo[0].granted,protoPayload.status.message)'
