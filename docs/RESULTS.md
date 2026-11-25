# 실무 워크플로 검증 결과

## 최종 결과물

**[파비 최종 납품본 6개 보기](cases/pabi/outputs/README.md)**

[파비 입력 자료](cases/pabi/inputs/README.md) · [정기배송 시연 납품본](cases/subscription-support/outputs/README.md)

## 실무에서 쓰는 방식

- 오너는 PM 창구에 목표와 완료 기준을 전달하고, PM 납품 보고에서 담당별 결과와 결정할 사항을 확인한다.
- PM은 작업별로 필요한 근거를 골라 배정한다. 직원은 선행 문서의 핵심 요약을 받고, QA는 수정 영향이 있는 산출물만 다시 검수해 반복 입력을 줄인다.

## 회귀 테스트

**20개 통과.** 작업별 근거 분리, 요약 인계, Markdown 필드, 수정 범위 재검수, 납품 보류와 토큰 기록을 확인했다.

```bash
python3 -m unittest discover -s hermes/tests -v
```

## 실제 모델 실행

Hermes 사용 기록에서 두 의뢰 모두 OpenAI Codex(`openai-codex`, `gpt-6-sol`)의 호출과 응답 완료를 확인했다.

| 의뢰 | 납품 결과 | 검증 |
| --- | --- | --- |
| 파비 개발·사업화 기획 | 교육·판매 2개 트랙의 Markdown 6편 | 근거 21개 분류 · QA 통과 · 모델 14회 호출 |
| [가상 커피 정기배송 시연](cases/subscription-support/inputs/README.md) | [상담 FAQ·답장 초안과 운영 개선안](cases/subscription-support/outputs/README.md) | Markdown 2편 QA 통과 · 모델 5회 호출 |

### 토큰 사용량

같은 의뢰 입력과 모델로 QA를 통과한 실행을 비교했다. 초안 입력은 작성 단계에 전달한 토큰이며, 전체는 PM·작성·QA 호출의 입력과 출력을 합산한 값이다.

| 의뢰 | 초안 작성 입력 토큰 | 전체 토큰 | 측정 기록 |
| --- | --- | --- | --- |
| 파비 | 26,424 → 14,608 · **44.7% 감소** | 98,923 → 80,635 · 18.5% 감소 | [파비 비교 기록](cases/pabi/execution/token-comparison.json) |
| 정기배송 | 5,972 → 4,812 · **19.4% 감소** | 19,569 → 18,576 · 5.1% 감소 | [정기배송 비교 기록](cases/subscription-support/execution/token-comparison.json) |

## 파비 개발·사업화 사례

파비는 앱과 음성 대화형 실물 기기를 함께 사용하는 K-pop 서비스 기획이다. 이 의뢰는 **정부지원사업용 한국어 교육 콘텐츠**와 **아리랑TV 협업 판매용 AI 굿즈**를 각각 검토했다. 교육 트랙은 초급 해외 팬의 한국어 발화를, 판매 트랙은 팬이 앱에 돌아오고 실물이나 구독에 비용을 낼 이유를 구체화했다. [의뢰서](cases/pabi/inputs/brief.md)

### 입력 자료

첨부 문서 네 편과 가공 회의록은 출처를 대조하는 자료다. 모델 실행에는 맡은 업무에 맞춰 구조화한 근거를 전달했다. [입력 자료 전체](cases/pabi/inputs/README.md)

| 자료 | 의뢰에 반영한 내용 |
| --- | --- |
| [(선도형) 콘진원 인공지능 콘텐츠 제작지원 기획서](cases/pabi/inputs/references/kocca-ai-content-proposal.md) | 교육 타깃과 콘텐츠 범위, 재사용 기술 후보, 방송·데이터 조건 |
| [(아리랑 파비) 아이디어 수집 3개](cases/pabi/inputs/references/arirang-pabi-ideas.md) | 팬레터, 팬 활동 기록, K-pop 한국어 학습 아이디어 |
| [[정부 제안 사업] 파비 대화인형](cases/pabi/inputs/references/government-pabi-brief.md) | tv파비를 활용한 글로벌 한국어 교육 방향 |
| [아이디어 구체화](cases/pabi/inputs/references/pabi-concept-details.md) | 앱·기기 기능, 주간 팬 경험, 파트너 자료와 음성 활용 조건 |
| [파비 회의록 1차 가공본](cases/pabi/inputs/references/meeting-clean.md) | 교육·판매 방향, 캐릭터 결정, 가격·구독 가설과 확인 사항 |

실제 입력은 [의뢰서](cases/pabi/inputs/brief.md), [트랙과 산출물 명세](cases/pabi/inputs/job.toml), [가공 근거 21개](cases/pabi/inputs/evidence.toml)로 구성된다. [실행 입력 스냅샷](cases/pabi/inputs/run-inputs.json)

### 역할별 작업과 결과물

| 역할 | 이번 의뢰에서 한 일 | 결과물과 기록 |
| --- | --- | --- |
| PM | 근거 21개를 교육 7개, 판매 10개, 공통 2개, 귀속 확인 2개로 나눴다. 작업별 담당과 근거를 정하고, 교육 파일럿과 오너 확인 사항을 작성했다. | [근거 분류·역할 배정](cases/pabi/execution/plan.json) · [교육 지원사업 기획 초안](cases/pabi/outputs/education-proposal.md) |
| 제작 | 초급 성인 팬이 가상 굿즈샵에서 응원봉 재고를 묻는 4턴 한·영 대화를 작성했다. 답변별 피드백과 재시도, 인식이 불확실할 때의 텍스트 선택을 포함했다. | [한국어 말하기 에피소드](cases/pabi/outputs/learning-episode.md) |
| 마케팅 | 구매·재방문·구독 이유를 나누어 판매 포인트를 정하고 일정·브랜드·답변지·음성·투표를 협의할 질문으로 정리했다. | [판매 포인트·구독 가설](cases/pabi/outputs/sales-positioning.md) · [파트너 협의표](cases/pabi/outputs/partner-checklist.md) |
| 제품기획 | 판매 포인트를 앱과 실물의 수용 기준으로 구체화하고, 판매 메시지·실물 수요·월 구독 의향을 각각 시험하는 안을 작성했다. | [앱·실물 MVP 기능 명세](cases/pabi/outputs/goods-mvp.md) · [구매·구독 실험안](cases/pabi/outputs/sales-experiments.md) |
| QA | 근거 배정과 산출물 6편을 검수했다. 교육 기획의 선행 문서 참조와 근거 표기를 보완하도록 요청했고, 이 파일을 다시 확인했다. | [분류 QA](cases/pabi/execution/review-routing-1.json) · [보완 의견](cases/pabi/execution/review-1.json) · [최종 재검수](cases/pabi/execution/review-3.json) |
| 고객 응대 | 파비 의뢰에서는 배정된 작업이 없었다. 별도 정기배송 의뢰에서 상담 FAQ와 운영 개선표를 작성했다. | [정기배송 의뢰 명세](../hermes/examples/subscription-support/job.toml) |

교육에서는 제작자의 에피소드 요약이 PM 기획으로 이어졌다. 판매에서는 제품기획이 판매 포인트 요약으로 MVP를 작성하고, 두 문서의 요약을 실험안에 반영했다. [산출물 선행 관계](cases/pabi/inputs/job.toml)

### 최종 결과

- **교육** — 해외 초급 팬이 굿즈샵에서 응원봉 재고와 수량을 묻는 상황극을 사용한다. 목표 표현을 다른 상황에서도 쓸 수 있는지 2주 동안 검증하고, 음성 입력은 선택으로 둔다. [학습 에피소드](cases/pabi/outputs/learning-episode.md) · [지원사업 기획 초안](cases/pabi/outputs/education-proposal.md)
- **판매** — 현지 시각 일정과 알림으로 앱의 반복 사용을 시험한다. 실물은 시제품과 가격을 본 뒤 알림을 신청하는 행동을, 구독은 앱을 반복 사용한 뒤 유료 시안에 보이는 관심을 측정한다. 협업 콘텐츠와 음성·투표 혜택은 권리·운영 확인 항목이다. [판매 포인트](cases/pabi/outputs/sales-positioning.md) · [MVP 명세](cases/pabi/outputs/goods-mvp.md) · [실험안](cases/pabi/outputs/sales-experiments.md) · [파트너 협의표](cases/pabi/outputs/partner-checklist.md)

매니저 콘셉트가 어느 사업에 적용되는지는 확인 대상으로 남겼다. 가격, 구매 전환, 학습 효과와 협업 권한은 후속 검증 항목이다. [실행 상태](cases/pabi/execution/run.json) · [작업별 모델 사용 기록](cases/pabi/execution/usage-summary.json)
