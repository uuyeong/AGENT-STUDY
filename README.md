# AGENT-STUDY: ODOC 에이전트 팀

**서로 일을 주고받으며 협업하는 세 명의 AI 에이전트 팀.**
Hermes에 프로필 3개로 올리고, 칸반 보드로 업무를 주고받게 했다.

```
오너 ─ 카드 2장 ─▶ [클라이언트] 고객 메일 처리 ── 버그·FAQ 공백·제휴 제안 ──▶
                  [PM] 회의록 + 보고로 칸반 작성 ── kanban_create ──▶ [마케팅] 블로그, 제휴 검토
                                                                ──▶ [클라이언트] FAQ 작성
                                                                ──▶ [PM] 최종 칸반 정리
```

| 항목 | 내용 |
|---|---|
| 에이전트 | PM(업무 배분, 칸반), 마케팅(홍보 초안), 클라이언트(고객 응대, FAQ) |
| 플랫폼 · 모델 | Hermes Agent v0.23.2 · Claude Opus 5.5 |
| 원리 | 프로필 = `SOUL.md`(인격) + `SKILL.md`(업무 매뉴얼) + `USER.md`(오너 정보). 협업은 칸반 카드와 완료 요약으로 |
| 데이터 | 직접 작성한 회의록, 제품 소개, FAQ, 고객 메일 5통 |
| 결과 | 카드 6장 중 4장을 PM이 직접 만들어 배분. handoffs 15건. 인젝션 메일 격리. 발송·게시 없음 |

## 문서
- [docs/STUDY.md](docs/STUDY.md): Claude와 Hermes의 역할, 실행 순서도, 스터디 노트
- [docs/DESIGN.md](docs/DESIGN.md): 설계, 원리, 기술 스택, 데이터
- [docs/RESULTS.md](docs/RESULTS.md): 실행 결과
- [docs/WORKLOG.md](docs/WORKLOG.md): 작업 과정

## 폴더 구조
```
agents/     공통 에이전트 정의 (SOUL, SKILL, USER)
data/       입력 데이터
hermes/     Hermes 버전: 협업 규칙, 프로필 설치, 팀 실행, 기록 내보내기, 작업 폴더
python/     Python 버전 (검증용): 협업 규칙, 실행기, 결과
docs/       문서
lecture/    로컬 강의 자료 (Git 추적 제외)
```

## 실행
Hermes를 설치하고 `hermes model`에서 Anthropic(Claude)을 고른 뒤 실행한다.
```bash
./hermes/setup_profiles.sh
```
```bash
./hermes/run_team.sh
```
```bash
hermes kanban --board odoc watch
```
```bash
python3 hermes/export_board.py
```
Python 버전은 아래 명령으로 실행한다.
```bash
python3 python/agent.py team
```
