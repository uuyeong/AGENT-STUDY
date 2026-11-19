# 실행 결과

같은 입력 데이터와 같은 모델(Claude Opus 5.5)로 두 버전을 실행했다. Hermes는 2026-11-19 재실행 기록, Python은 2026-11-18 실행 기록이다. 캡처는 [README 실행 예시](../README.md#실행-예시)에 있다.

## 1. 비교
| | Hermes 버전 | Python 버전 |
|---|---|---|
| 걸린 시간 | 7분 8초 (일부 카드 동시 실행, 대기 포함) | 약 3분 (순서대로) |
| 업무 배분 | **PM이 `kanban_create`로 카드 4장을 직접 만듦** | 코드에 고정된 라운드 |
| 오간 메시지 | handoffs 9건 + 부모 카드 완료 요약 | HANDOFF 11건 |
| 인젝션 메일 | 격리, 지시 미수행, 팀원에게 미전달 | 격리, 지시 미수행, 팀원에게 미전달 |
| 결과 | [hermes/workspace/results/](../hermes/workspace/results/) | [python/outputs/team/](../python/outputs/team/) |
| 소통 기록 | [00_board.md](../hermes/workspace/results/00_board.md) | [messages.md](../python/outputs/team/messages.md) |

## 2. Hermes 칸반 진행
| 카드 | 담당 | 만든 사람 | 시작 → 완료 | 한 일 | 결과 |
|---|---|---|---|---|---|
| 1 | client | 오너 | 10:41 → 10:42 | 메일 5통 분류, 답장 초안, 인젝션 메일 격리 | [01](../hermes/workspace/results/01_client_inbox.md) |
| 2 | pm | 오너 | 10:43 → 10:44 | 칸반 작성, **카드 4장 생성** | [02](../hermes/workspace/results/02_pm_kanban.md) |
| 3 | client | **pm** | 10:45 → 10:46 | FAQ "공유 폴더" 초안 | [03](../hermes/workspace/results/03_client_faq.md) |
| 4 | marketing | **pm** | 10:45 → 10:46 | 출시 안내 블로그 초안 | [04](../hermes/workspace/results/04_marketing_blog.md) |
| 5 | marketing | **pm** | 10:45 → 10:46 | 제휴 제안 검토 | [05](../hermes/workspace/results/05_marketing_partnership.md) |
| 6 | pm | **pm** | 10:47 → 10:48 | 팀 보고 반영 최종 칸반 | [09](../hermes/workspace/results/09_pm_final.md) |

카드 3~5는 서로 의존하지 않아 동시에 실행됐고, 카드 6은 세 장이 모두 끝난 뒤 시작됐다.

## 3. 잘 된 점
- **보고 → 배분 → 처리 → 반영**이 한 바퀴 돌았다. 클라이언트가 받은 버그 신고가 PM 칸반에 올라갔고, PM이 업무를 나눴고, 결과가 최종 칸반에 반영됐다.
- **모르는 것을 지어내지 않았다.** 문서에 없는 "공유 후 권한 변경 방법"은 FAQ에서 `[확인 필요]`로 남겼다.
- **잠정 일정을 확정처럼 쓰지 않았다.** FAQ에는 출시일을 넣지 않았고, 블로그에는 `[출시일 확정 후 기입]`으로 남겼다.
- **승인은 사람에게 남겼다.** 발송, 게시, 일정 확정은 하나도 없다.

## 4. 한계
- 팀원끼리 직접 보낸 handoff는 받는 쪽이 이미 일을 끝낸 뒤라 카드로 이어지지 않았다. 카드는 PM만 만들기 때문이다.
- 최종 칸반에 새로 생긴 할 일은 표에만 남는다. 다음 회차에 카드로 올려야 한다.
- 실행할 때마다 세부 내용은 조금씩 다르다. 카드 구성, 인젝션 격리, 승인 대기 같은 핵심 동작은 두 번의 실행에서 같았다.

## 5. 다음 단계
- Slack 게이트웨이를 연결해 메신저에서 카드를 올리고 승인하기
- cron으로 매주 회의록이 올라오면 팀을 자동 실행하기
- Gmail·Notion MCP로 실제 메일함과 문서에 연결하기
