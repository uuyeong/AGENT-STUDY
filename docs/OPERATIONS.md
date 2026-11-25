# Hermes 실무 운영

## 의뢰 자료 준비

`hermes/jobs/<의뢰-id>/`에 가공한 자료를 저장한다. 회의 원문은 의뢰 폴더에 넣지 않는다. 불필요한 발언과 개인 식별 정보를 제거하고, 근거 행마다 한 가지 사실·결정·제안과 출처를 남긴다. 의뢰 폴더는 Git에서 제외된다.

| 파일 | 작성할 내용 |
| --- | --- |
| `brief.md` | 의뢰 목표, 제약, 납품물 용도 |
| `job.toml` | 트랙과 산출물별 독자, 목적, 검수 기준 |
| `evidence.toml` | 가공 근거의 고유 ID, 상태, 출처와 요약 |

모델에 전달할 수 있는 자료만 입력한다. 실행 시 가공 자료가 OpenAI Codex에 전달되며 실행 기록과 Hermes 대화에 남을 수 있다. [가상 정기배송 의뢰 예제](../hermes/examples/subscription-support/)

### 입력 항목

- `job.toml`의 최상위에 `title`을 적는다. `[[tracks]]`의 필수 항목은 `id`, `label`, `objective`다. 트랙마다 산출물을 하나 이상 지정한다.
- `[[outputs]]`의 필수 항목은 `id`, `track`, `audience`, `goal`, `checks`다. `checks`는 관찰 가능한 통과 기준의 문자열 배열이다.
- `needs`, `format`, `columns`는 선택 항목이다. `needs`의 선행 산출물은 핵심 요약으로 전달한다. 납품 형식은 Markdown이며 `columns`는 항목별 필드명과 순서를 정한다. `format = "csv"`가 있는 의뢰서도 해당 필드를 Markdown으로 렌더링한다.
- `[[evidence]]`의 필수 항목은 `id`, `source`, `summary`, `status`다. 상태는 사실 `fact`, 내부 결정 `decision`, 제안 `proposal`, 확인 대기 `open` 중 하나다.
- ID에는 소문자 영숫자와 하이픈을 사용한다. 산출물 ID는 의뢰 안에서 유일해야 한다.

## 실행

```bash
python3 hermes/run_work.py <의뢰-id> --check
python3 hermes/run_work.py <의뢰-id>
```

`--check`는 모델을 호출하지 않고 입력을 검증한다. 실행의 기본값은 Hermes `default` 프로필과 OpenAI Codex `gpt-6-sol`이다. 프로필과 모델은 `--profile`, `--model`로 지정한다. 인증 상태는 `hermes -p <프로필> auth status openai-codex`로 확인한다.

| 실행 폴더 항목 | 쓰임 |
| --- | --- |
| `inputs.json` | 해당 실행에 사용한 가공 입력 |
| `plan.json`, `replan.json` | 근거 귀속, 작업별 근거 ID, 담당 역할과 오너 확인 사항 |
| `review-routing-*.json` | 작성 전 근거 귀속 검수 |
| `drafts/`, `review-<회차>.json` | Markdown 작성본과 해당 회차의 QA 대상·수정 의견 |
| `usage/`, `usage-summary.json`, `run.json` | Hermes 사용 기록, 역할별 입력·출력 토큰과 실행 상태 |
| `delivery/README.md` | QA를 통과한 납품물, 담당 역할, 오너 확인 사항 |

오류가 나면 실행 폴더의 상태와 사용 기록을 확인한다. 다시 실행하면 별도 실행 폴더가 생긴다. 기기 동작, 계약, 제출 자격 등 실무 확인이 남은 항목은 산출물에 표시한다.

## 칸반으로 접수 추적

`bash hermes/submit_work.sh <의뢰-id> "<제목>"`은 `odoc-work`에 `blocked` 상태로 접수한다. `--example`을 붙이면 `odoc-test`에 접수한다. 같은 보드에서 의뢰 ID당 카드 하나를 사용한다. 모델 실행은 `run_work.py`로 시작한다. [칸반 워커 팀 규칙](../hermes/TEAM.md)
