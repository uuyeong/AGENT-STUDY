# AGENT-STUDY: ODOC 에이전트 팀

PM·마케팅·고객 응대 에이전트가 Hermes 칸반에서 업무를 나눠 처리한다.

## 실행 명령어

프로젝트 루트에서 실행한다.

```bash
# Hermes
./hermes/run_team.sh
hermes kanban --board odoc watch
```

```bash
# Python 검증용
python3 python/agent.py team
```

## Example

### 예시 입력

```text
회의록 발췌
- 개발은 이번 주 금요일(11/20)까지 마무리하기로 함. 담당 이도윤.
- 출시 안내 블로그 글 초안을 최하늘이 11/23까지 작성.
- FAQ에 "공유 폴더" 항목 추가 필요 (담당, 마감 미정).

고객 메일 발췌
안드로이드에서 공유 폴더를 열면 앱이 바로 종료됩니다. 버전은 3.2.1이에요. 급합니다.

업무 요청 요약
고객 메일을 분류해 답장 초안을 작성하고, 회의록과 고객 응대 보고를 바탕으로 후속 업무를 배분해. 팀원 작업이 끝나면 최종 칸반에 반영해.
```

입력 원문 · [회의록](data/meeting_notes.txt) · [고객 메일](data/client_emails.txt) · [제품 소개](data/product_brief.txt) · [FAQ](data/faq.md)

### 예시 출력

고객 응대가 앱 종료 신고를 PM에게 넘겼다. PM은 이를 우선순위 `P0`으로 표시하고 FAQ·블로그·제휴 검토 결과를 최종 칸반에 반영했다.

![PM이 작성한 최종 칸반](docs/images/pm-final.png)

[최종 칸반 원문](hermes/workspace/results/09_pm_final.md) · [고객 메일 분류 캡처](docs/images/client-result.png) · [Hermes 완료 카드 캡처](docs/images/kanban-done.png)
