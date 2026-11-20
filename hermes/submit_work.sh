#!/usr/bin/env bash
# 실무 의뢰 또는 예제를 모델 호출 없이 Hermes 칸반에 접수한다.
set -euo pipefail

BOARD="odoc-work"
BOARD_NAME="ODOC 실무"
BODY="brief.md의 의뢰를 읽고 담당 업무와 검수 조건을 정리하세요. 산출물은 results/에 저장하세요."
if [[ ${1:-} == --example ]]; then
  BOARD="odoc-test"
  BOARD_NAME="ODOC 예제와 테스트"
  BODY="brief.md를 테스트 입력으로 사용하세요. 역할별 기대 결과를 검토하고 검증 기록을 results/에 저장하세요. 참조 제품은 읽기 전용입니다."
  shift
fi

if [[ $# -ne 2 || ! $1 =~ ^[a-z0-9]+(-[a-z0-9]+)*$ || -z ${2//[[:space:]]/} ]]; then
  echo "사용법: bash hermes/submit_work.sh [--example] <업무-id> <제목>" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JOB_ID="$1"
WORKSPACE="$ROOT/hermes/jobs/$JOB_ID"

if [[ ! -f "$WORKSPACE/brief.md" || ! -s "$WORKSPACE/brief.md" ]]; then
  echo "의뢰서를 작성하세요: $WORKSPACE/brief.md" >&2
  exit 2
fi

mkdir -p "$WORKSPACE/results"
hermes kanban boards create "$BOARD" --name "$BOARD_NAME" >/dev/null
# Hermes의 triage는 게이트웨이가 자동으로 모델에 전달할 수 있다.
hermes kanban --board "$BOARD" create "$2" \
  --initial-status blocked --assignee pm --workspace "dir:$WORKSPACE" \
  --idempotency-key "$JOB_ID" \
  --body "$BODY" \
  --json
