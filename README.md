# AGENT-STUDY · Hermes 실무 에이전트 팀

OpenAI Codex(`gpt-6-sol`)로 의뢰의 근거를 분류하고, 역할별로 산출물을 작성해 QA 후 납품합니다.

## 터미널 시연

프로젝트 루트에서 아래 명령을 실행합니다. 터미널에 근거 분류, 역할별 작성, QA 진행 단계가 표시됩니다.

```bash
mkdir -p hermes/jobs/subscription-demo &&
  cp hermes/examples/subscription-support/{brief.md,job.toml,evidence.toml} hermes/jobs/subscription-demo/ &&
  python3 hermes/run_work.py subscription-demo --check &&
  demo_index="$(python3 hermes/run_work.py subscription-demo)" &&
  printf '%s\n' "$demo_index" &&
  cat "$demo_index"
```

## 시연 입력

가상의 커피 정기배송 사례입니다. 운영 정책과 고객 문의 4건으로 상담 답장과 운영 개선표를 작성합니다.

| 파일 | 내용 |
| --- | --- |
| [brief.md](hermes/examples/subscription-support/brief.md) | 의뢰의 목적과 문의 표본을 해석할 범위 |
| [job.toml](hermes/examples/subscription-support/job.toml) | 작성할 산출물, 독자, QA 기준과 선행 관계 |
| [evidence.toml](hermes/examples/subscription-support/evidence.toml) | 배송·결제 정책과 가상 문의 4건의 근거 |

## 결과 확인

QA를 통과하면 명령이 납품 목록 경로와 내용을 표시합니다. 같은 폴더에 `support-faq.md`(상담 FAQ·답장 초안)와 `support-actions.csv`(운영 개선표)가 있습니다.

```text
hermes/jobs/subscription-demo/runs/<실행-id>/delivery/
```

[시연 실행에서 나온 납품본](docs/cases/subscription-support/outputs/README.md)

[설계와 역할](docs/DESIGN.md) · [운영 절차](docs/OPERATIONS.md) · [실행 결과](docs/RESULTS.md)
