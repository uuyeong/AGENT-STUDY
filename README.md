# AGENT-STUDY · Hermes 실무 에이전트 팀

Hermes와 OpenAI Codex로 제품 기획, 사업화, 고객 응대, 콘텐츠 제작 의뢰를 처리합니다. PM이 가공 근거를 트랙별로 분류하고 담당 역할을 배정합니다. QA를 통과한 결과는 Markdown 또는 CSV로 납품합니다.

## 처음 실행하기

Python 3.11 이상과 `--safe-mode`, `--toolsets`, `--usage-file`을 지원하는 Hermes CLI가 필요합니다. Hermes 기본 프로필에 OpenAI Codex로 로그인한 후 프로젝트 루트에서 실행합니다.

```bash
mkdir -p hermes/jobs/subscription-support
cp -n hermes/examples/subscription-support/{brief.md,job.toml,evidence.toml} hermes/jobs/subscription-support/
python3 hermes/run_work.py subscription-support --check
python3 hermes/run_work.py subscription-support
```

마지막 명령은 `hermes/jobs/<의뢰-id>/runs/<실행-id>/delivery/README.md` 경로를 출력합니다.

## 실무에 사용하기

1. 회의록과 문서를 출처가 있는 사실·결정·제안·확인 사항으로 가공합니다.
2. `hermes/jobs/<의뢰-id>/`에 `brief.md`, `job.toml`, `evidence.toml`을 작성합니다. 의뢰별 트랙, 산출물, 독자, 검수 기준을 지정합니다.
3. `--check`로 입력을 검증한 뒤 실행합니다. 칸반 추적이 필요하면 `hermes/submit_work.sh`로 접수합니다.
4. 납품 목록과 QA 기록을 검토합니다. 외부 발송·게시·제출은 오너가 결정합니다.

- [입력 형식과 운영 절차](hermes/OPERATIONS.md)
- [실행 설계와 역할](docs/DESIGN.md)
- [검증 결과와 산출물](docs/RESULTS.md)

## 회귀 테스트

```bash
python3 -m unittest discover -s hermes/tests -v
```
