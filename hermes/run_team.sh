#!/usr/bin/env bash
# Hermes 칸반으로 에이전트 팀을 돌린다.
#   오너(사람)는 시작 카드 2장만 올리고, 나머지는 에이전트가 칸반에서 스스로 진행한다.
#   1) client: 고객 메일 처리
#   2) pm: 회의록 + client의 handoffs로 칸반 작성 → kanban_create로 팀원에게 업무 배분
# 진행 상황: hermes kanban --board odoc watch   /   hermes dashboard → Kanban
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WS="$ROOT/hermes/workspace"
BOARD="odoc"

# 작업 폴더 준비 (원본 데이터 복사, 결과 폴더 비우기)
mkdir -p "$WS/data" "$WS/results"
cp "$ROOT"/data/* "$WS/data/"
rm -f "$WS"/results/*.md

# 보드 준비
hermes kanban boards list 2>/dev/null | grep -q "$BOARD" || \
  hermes kanban boards create "$BOARD" --name "ODOC Team" --description "PM · 마케팅 · 클라이언트 에이전트 팀"

K="hermes kanban --board $BOARD"
W="dir:$WS"

# 이전 회차 카드는 보관(archive) 처리해 이번 회차만 보이게 한다 (기록은 DB에 남음)
OLD=$($K list --json | python3 -c 'import json,sys; d=json.load(sys.stdin); d=d if isinstance(d,list) else d.get("tasks",[]); print(" ".join(t["id"] for t in d))')
[ -n "$OLD" ] && $K archive $OLD >/dev/null

T1=$($K create "고객 메일 분류와 답장 초안" --assignee client --workspace "$W" --priority 2 --json --body \
"client-inbox-router 스킬대로 data/client_emails.txt 를 data/faq.md 기준으로 분류하고 답장 초안을 써 줘. 보내지는 마.
결과는 results/01_client_inbox.md 에 저장해.
버그 신고, FAQ로 답하지 못한 질문, 제휴 제안은 kanban_complete 의 metadata.handoffs 로 해당 팀원에게 넘겨." \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

T2=$($K create "회의록 칸반 정리와 업무 배분" --assignee pm --parent "$T1" --workspace "$W" --priority 2 --json --body \
"meeting-to-kanban 스킬대로 data/meeting_notes.txt 를 칸반으로 정리하고 results/02_pm_kanban.md 에 저장해.
부모 카드(client)의 metadata.handoffs 중 pm에게 온 내용도 칸반에 반영해.
그다음 너는 오케스트레이터로서 kanban_create 로 업무를 배분해:
 - 다른 팀원 역할에 맞는 일(블로그는 marketing, FAQ·고객 답변은 client, client가 marketing에게 넘긴 제휴 건 등)마다 카드 1장.
   각 카드에 workspace='$W', 결과 파일 경로(results/03_..., results/04_...)와 맥락을 body에 적어.
 - 마지막으로 너 자신(pm)에게 '팀 보고 반영 최종 칸반' 카드를 만들고, 위 카드들을 parents 로 연결해.
   그 카드 body에는 '팀원 완료 요약을 반영해 results/09_pm_final.md 에 최종 칸반을 저장하고, 새 카드는 만들지 말 것'이라고 적어." \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

echo "시작 카드: client=$T1, pm=$T2 (pm은 client 완료 후 시작)"
$K dispatch >/dev/null 2>&1 || true   # 디스패처 즉시 한 번 실행 (이후는 게이트웨이가 60초마다)
$K list
