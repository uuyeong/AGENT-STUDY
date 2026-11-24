# 실무 워크플로 검증 결과

## 회귀 테스트

**16개 통과.** 칸반 접수, 입력 검증, 트랙별 근거 분리, CSV 검증, QA 보완과 납품 보류, 모델 사용 기록 검증을 확인했다.

```bash
python3 -m unittest discover -s hermes/tests -v
```

## 실제 모델 실행

Hermes 사용 기록에서 두 의뢰의 OpenAI Codex(`gpt-6-sol`) 호출과 응답 완료를 확인했다.

| 의뢰 | 납품 결과 | 검증 |
| --- | --- | --- |
| [가상 커피 정기배송 고객 문의](../hermes/examples/subscription-support/) | 상담 FAQ·답장 초안(Markdown), 운영 개선표(CSV) | QA 통과 · Codex 11회 호출 |
| 비공개 제품 기획 의뢰 | 교육 기획, 학습 에피소드, 판매 포인트, 앱·기기 MVP, 제휴 확인표(Markdown), 구매·구독 실험표(CSV) | 가공 근거 21개 분류 · 2개 트랙 QA 통과 · Codex 13회 호출 |

납품 목록은 각 실행의 `delivery/README.md`에 있다. 검수 의견과 모델 사용 기록은 같은 실행 폴더에서 확인할 수 있다.
