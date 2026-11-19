# AGENT-STUDY: ODOC 에이전트 팀

**서로 일을 주고받으며 협업하는 세 명의 AI 에이전트 팀.**
Hermes에 프로필 3개로 올리고, 칸반 보드로 업무를 주고받게 했다.

```text
고객 메일 처리 → PM이 회의록과 보고로 업무 배분 → 마케팅·클라이언트 작업 → PM 최종 정리
```

| 항목 | 내용 |
|---|---|
| 에이전트 | PM(업무 배분, 칸반), 마케팅(홍보 초안), 클라이언트(고객 응대, FAQ) |
| 플랫폼 · 모델 | Hermes Agent v0.23.2 · Claude Opus 5.5 |
| 원리 | Claude가 계획·내용을 작성하고, Hermes가 역할별 호출·도구 실행·작업 진행을 관리 |
| 데이터 | 직접 작성한 회의록, 제품 소개, FAQ, 고객 메일 5통 |
| 결과 | 카드 6장 중 4장을 PM이 직접 만들어 배분. handoffs 15건. 인젝션 메일 격리. 발송·게시 없음 |

## 실행하기 (Hermes)

Hermes, Claude 인증, 게이트웨이, `pm`·`marketing`·`client` 프로필이 준비된 환경을 기준으로 한다.

프로젝트 폴더에서 실행한다. 기본 명령은 저장소에 들어 있는 샘플 자료와 요청을 사용한다.

```bash
cd ~/Developer/AGENT-STUDY
./hermes/run_team.sh
hermes kanban --board odoc watch
```

`watch`는 진행 상황을 계속 보여 준다. 모든 작업이 완료되면 `Ctrl+C`로 종료한다.
재실행하면 이전 카드는 보관 처리되고, `hermes/workspace/results/`의 결과 문서는 새로 작성된다.

## 회의록과 요청 입력하기

현재 버전은 **파일에 자료를 넣고, 실행 스크립트에 요청을 적은 뒤 실행**하는 방식이다.

| 입력 파일 | 넣을 내용 |
|---|---|
| [data/meeting_notes.txt](data/meeting_notes.txt) | 회의록: 할 일, 담당자, 마감, 결정·미정 사항 |
| [data/client_emails.txt](data/client_emails.txt) | 분류하고 답할 고객 메일 |
| [data/product_brief.txt](data/product_brief.txt) | 마케팅·FAQ 작성에 사용할 제품 정보 |
| [data/faq.md](data/faq.md) | 고객 답변의 근거가 되는 정책과 사용법 |

예를 들어 회의록은 아래 파일을 열어 내용을 바꾸고 저장한다.

```bash
nano data/meeting_notes.txt
```

업무 요청은 [hermes/run_team.sh](hermes/run_team.sh)의 두 시작 카드에 있는 `--body` 문자열을 수정한다.

- **고객 메일 분류와 답장 초안:** 고객 응대 에이전트에게 줄 요청
- **회의록 칸반 정리와 업무 배분:** PM에게 줄 요청

```bash
nano hermes/run_team.sh
```

예를 들어 PM 요청의 첫 문장을 다음처럼 바꿀 수 있다.

```text
meeting-to-kanban 스킬대로 data/meeting_notes.txt 에서 할 일·담당자·마감을 뽑아 긴급한 순서로 results/02_pm_kanban.md 에 정리해.
```

파일 경로와 뒤에 이어지는 업무 배분·최종 정리 카드 생성 지시는 유지한다. 저장 후 `./hermes/run_team.sh`를 다시 실행한다.
입력 자료는 `data/`에서 수정한다. `hermes/workspace/data/`는 실행할 때 복사되는 사본이다.

## 결과 확인하기

작업 완료 후 카드 상태를 확인하고, 보드 기록을 파일로 내보낸다.

```bash
hermes kanban --board odoc list
python3 hermes/export_board.py
```

- [보드 기록](hermes/workspace/results/00_board.md): 카드, 담당자, 완료 요약, 인계 내용
- [최종 칸반](hermes/workspace/results/09_pm_final.md): PM이 팀원 결과를 종합한 최종 문서
- [전체 결과](hermes/workspace/results/): 메일 분류·답장, FAQ, 블로그, 제휴 검토

## Python 실행과 무엇이 다른가

같은 `agents/`의 역할·매뉴얼과 `data/`의 입력 자료를 사용하며, **실행을 관리하는 프로그램이 다르다.**

| 구분 | Hermes 버전 (주 버전) | Python 버전 (검증용) |
|---|---|---|
| 실행 명령 | `./hermes/run_team.sh` | `python3 python/agent.py team` |
| 실행 관리자 | Hermes 프로필·칸반 | 직접 작성한 `python/agent.py` |
| 업무 순서 | PM 역할의 Claude가 카드를 만들고 Hermes가 의존관계에 따라 실행 | 코드에 정한 4라운드를 순서대로 실행 |
| 결과 전달 | 카드의 완료 요약·인계 내용 | 출력의 `HANDOFF`를 Python이 읽어 전달 |
| 파일 처리 | Claude가 도구를 요청하면 Hermes가 읽기·저장을 실행 | Python이 입력을 읽어 모델에 넣고 응답을 저장 |
| 결과 위치 | `hermes/workspace/results/` | `python/outputs/team/` |

Python 버전은 Hermes를 거치지 않고 Claude Code CLI 또는 Anthropic SDK로 모델을 호출한다. 기본 흐름은 다음 명령으로 실행한다.

```bash
python3 python/agent.py team
```

입력 자료는 같은 `data/` 파일을 수정한다. Python 버전의 기본 요청은 [python/agent.py](python/agent.py)의 `SAMPLES`, 라운드별 후속 요청은 `team()`에 있다.
회의록 정리만 따로 시험하려면 `python3 python/agent.py pm`을 실행한다. 이 명령은 다른 팀원까지 실행하지 않는다.

## 문서

- [docs/STUDY.md](docs/STUDY.md): Claude와 Hermes의 역할, 실행 순서도, 스터디 노트
- [docs/DESIGN.md](docs/DESIGN.md): 설계, 원리, 기술 스택, 데이터
- [docs/RESULTS.md](docs/RESULTS.md): 실행 결과
- [docs/WORKLOG.md](docs/WORKLOG.md): 작업 과정

## 폴더 구조

```text
agents/     공통 에이전트 정의 (SOUL, SKILL, USER)
data/       입력 데이터
hermes/     Hermes 협업 규칙, 프로필 설정·실행 스크립트, 작업 폴더
python/     Python 검증용 실행기와 결과
docs/       문서
lecture/    로컬 강의 자료 (Git 추적 제외)
```
