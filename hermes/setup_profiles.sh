#!/usr/bin/env bash
# agents/ 폴더의 실무 팀을 Hermes 프로필로 옮긴다.
#   모델 설정: OpenAI Codex / gpt-6-sol (MODEL 환경변수로 변경 가능)
#   SOUL.md           → ~/.hermes/profiles/<id>/SOUL.md
#   USER.md           → ~/.hermes/profiles/<id>/memories/USER.md  (Hermes 메모리 형식: 항목을 § 로 구분)
#   SKILL.md          → ~/.hermes/profiles/<id>/skills/team/<스킬이름>/SKILL.md
#   hermes/TEAM.md(칸반 협업 규칙) → 각 SKILL.md 뒤에 붙임
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
MODEL="${MODEL:-gpt-6-sol}"

case "$MODEL" in
  gpt-*) ;;
  *) echo "MODEL에는 OpenAI Codex의 gpt- 모델 ID를 사용하세요." >&2; exit 2 ;;
esac

skill_info() {  # id → "스킬이름|설명"
  case "$1" in
    pm)        echo "meeting-to-kanban|회의록이나 팀원 보고를 받아 칸반으로 정리하고 팀원에게 업무를 배분할 때" ;;
    marketing) echo "product-to-campaign|제품 정보나 pm의 요청을 받아 홍보 문구, 블로그, SNS 초안을 만들 때" ;;
    client)    echo "client-inbox-router|고객 메일을 분류하고 FAQ 기반 답장 초안을 쓰거나 FAQ 항목을 작성할 때" ;;
    producer)  echo "content-production|제품 자료와 기획을 화면 문구, 사용 안내, 촬영안으로 제작할 때" ;;
    qa)        echo "product-qa|제품 기획과 제작물이 실제 동작 및 제품 기준과 일치하는지 확인할 때" ;;
  esac
}

for id in pm marketing client producer qa; do
  dir="$HERMES_HOME/profiles/$id"
  if [ ! -d "$dir" ]; then
    hermes profile create "$id" --no-credentials --no-alias
  else
    echo "[$id] 프로필이 이미 있어 파일만 갱신함"
  fi

  hermes -p "$id" config set fallback_providers '[]' >/dev/null
  hermes -p "$id" config set fallback_model '[]' >/dev/null
  hermes -p "$id" config set model.provider openai-codex >/dev/null
  hermes -p "$id" config set model.default "$MODEL" >/dev/null

  cp "$ROOT/agents/$id/SOUL.md" "$dir/SOUL.md"
  mkdir -p "$dir/memories"
  # agents/USER.md 의 "- " 항목들을 Hermes 메모리 형식(항목 사이 §)으로 바꿔 넣는다
  grep '^- ' "$ROOT/agents/USER.md" | sed 's/^- //' | awk 'NR>1{print "§"} {print}' > "$dir/memories/USER.md"
  rm -f "$dir/USER.md"   # 예전 버전이 프로필 루트에 두던 사본 정리 (Hermes는 이 위치를 읽지 않음)

  info="$(skill_info "$id")"; skill="${info%%|*}"; desc="${info#*|}"
  sdir="$dir/skills/team/$skill"
  mkdir -p "$sdir"
  {
    printf -- '---\nname: %s\ndescription: %s\n---\n\n' "$skill" "$desc"
    cat "$ROOT/agents/$id/SKILL.md"
    printf '\n\n---\n\n'
    cat "$ROOT/hermes/TEAM.md"
  } > "$sdir/SKILL.md"

  echo "[$id] 완료 → $dir"
done

echo
hermes profile list
