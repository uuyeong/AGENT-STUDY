# 실무 워크플로 검증 결과

## 최종 결과물

**[파비 최종 납품본 6개 보기](cases/pabi/outputs/README.md)**

[파비 입력 자료](cases/pabi/inputs/README.md) · [정기배송 시연 납품본](cases/subscription-support/outputs/README.md)

## 회귀 테스트

**16개 통과.** 칸반 접수, 입력 형식과 선행 관계 검증, 트랙별 근거 분리, CSV 검증, QA 보완과 납품 보류, 모델 사용 기록 검증을 확인했다.

```bash
python3 -m unittest discover -s hermes/tests -v
```

## 실제 모델 실행

Hermes 사용 기록에서 두 의뢰 모두 OpenAI Codex(`openai-codex`, `gpt-6-sol`)의 호출과 응답 완료를 확인했다.

| 의뢰 | 납품 결과 | 검증 |
| --- | --- | --- |
| 파비 개발·사업화 기획 | 교육·판매 2개 트랙에서 Markdown 다섯 편과 CSV 한 편 | 근거 21개 분류 · QA 통과 · 모델 13회 호출 |
| [가상 커피 정기배송 시연](cases/subscription-support/inputs/README.md) | [상담 FAQ·답장 초안과 운영 개선표](cases/subscription-support/outputs/README.md) | QA 통과 · 모델 5회 호출 |

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
| PM | 근거 21개를 교육 전용 7개, 판매 전용 8개, 공통 5개, 귀속 확인 1개로 분류했다. 제작자의 에피소드를 반영해 교육 목표와 2주 파일럿을 기획했다. | [근거 분류·역할 배정](cases/pabi/execution/plan.json) · [교육 지원사업 기획 초안](cases/pabi/outputs/education-proposal.md) |
| 제작 | 초급 성인 팬이 가상 굿즈샵에서 물건의 위치를 묻는 4턴 한·영 대화를 작성했다. 답변별 피드백과 재시도, 음성 인식 불확실 시 문장 입력을 포함했다. | [한국어 말하기 에피소드](cases/pabi/outputs/learning-episode.md) |
| 마케팅 | 구매·재방문·구독 이유를 분리해 판매 포인트를 우선순위로 정했다. 앱·실물 명세를 참고해 구매·구독 실험을 설계하고, 일정·브랜드·답변지·음성·투표에 관한 협의 질문을 정리했다. | [판매 포인트·구독 가설](cases/pabi/outputs/sales-positioning.md) · [구매·구독 실험표](cases/pabi/outputs/sales-experiments.csv) · [파트너 협의표](cases/pabi/outputs/partner-checklist.md) |
| 제품기획 | 판매 포인트를 앱 선행 범위와 실물 검증으로 구체화했다. 현지 시간대 알림, 출처·갱신 시각, 정정·취소, 방해금지, 오프라인·미연결 상태를 기능별 수용 기준으로 정했다. | [앱·실물 MVP 기능 명세](cases/pabi/outputs/goods-mvp.md) |
| QA | 근거 분류를 먼저 확인한 뒤 각 트랙의 산출물을 검수했다. 구독 가격을 제시할 때 비교할 혜택이 모호하다고 지적했다. 마케팅이 월간 팬 활동 회고 카드 후보와 테스트 착수 조건을 명시한 뒤 6개 산출물이 통과했다. | [분류 QA](cases/pabi/execution/review-routing-1.json) · [보완 의견](cases/pabi/execution/review-1.json) · [최종 QA](cases/pabi/execution/review-2.json) |
| 고객 응대 | 파비 의뢰에서는 배정된 작업이 없었다. 별도 정기배송 의뢰에서 상담 FAQ와 운영 개선표를 작성했다. | [정기배송 의뢰 명세](../hermes/examples/subscription-support/job.toml) |

교육 트랙에서는 제작자의 에피소드가 PM 기획의 학습 과제로 이어졌다. 판매 트랙에서는 마케팅의 판매 포인트를 제품기획이 MVP 명세로 구체화했고, 마케팅이 두 문서를 바탕으로 실험표를 작성했다. [산출물 선행 관계](cases/pabi/inputs/job.toml)

### 최종 결과

- **교육** — 해외 초급 팬이 굿즈샵에서 정중히 위치를 묻고, 다른 장면에서도 목표 표현을 쓸 수 있는지 2주 동안 검증하는 안이다. 앱은 연습·기록을 맡고, tv파비는 선택형 음성 경험으로 검토한다. [학습 에피소드](cases/pabi/outputs/learning-episode.md) · [지원사업 기획 초안](cases/pabi/outputs/education-proposal.md)
- **판매** — 관심 아티스트의 현지 시각 일정과 리마인드로 앱의 반복 사용부터 시험한다. 실물은 소장성과 화면을 조작하지 않고 알림·대화를 이용하는 경험을, 구독은 월간 팬 활동 회고 카드를 각각 가설로 검증한다. 협업 콘텐츠와 음성·투표 혜택은 권리·운영 확인 항목으로 명시했다. [판매 포인트](cases/pabi/outputs/sales-positioning.md) · [MVP 명세](cases/pabi/outputs/goods-mvp.md) · [실험표](cases/pabi/outputs/sales-experiments.csv) · [파트너 협의표](cases/pabi/outputs/partner-checklist.md)

매니저 콘셉트가 어느 사업에 적용되는지는 확인 대상으로 남겼다. 가격, 구매 전환, 학습 효과와 협업 권한은 후속 검증 항목이다. [실행 상태](cases/pabi/execution/run.json) · [작업별 모델 사용 기록](cases/pabi/execution/usage-summary.json)
