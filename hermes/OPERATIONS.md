# Hermes 실무 운영

## 의뢰 접수와 납품

1. `hermes/jobs/<업무-id>/brief.md`에 사용자 문제, 할 일, 기준 자료, 완료 조건과 납품 형식을 적는다.
2. `bash hermes/submit_work.sh <업무-id> "<제목>"`으로 `odoc-work`에 접수한다. 카드는 수동 검토 대기(`blocked`) 상태에서 시작한다. 동일 ID로 다시 접수하면 기존 카드 ID를 돌려준다.
3. PM은 작업을 배분하고 선후 관계를 연결한다. 업무별 결과는 해당 의뢰 폴더의 `results/`에 두고, QA의 수정 요청은 담당 카드에 기록한다.
4. PM은 결과물 경로, 검증 증거, 오너 결정 사항을 함께 전달한다. 게시, 외부 발송, GitHub 이슈 등록과 실제 배포는 오너 승인 후 진행한다.

### 모델

`setup_profiles.sh`는 팀 프로필 다섯 개에 OpenAI Codex 모델을 지정하고 모델 fallback을 비운다. 실무 접수 명령은 카드에 자료 위치만 연결한다. Hermes 게이트웨이는 `triage` 카드를 기본 프로필의 보조 모델로 자동 분해할 수 있으므로 수동 접수는 `blocked`를 사용한다. 자동 실행을 시작하기 전에 실행 프로필의 OpenAI Codex 인증(`hermes -p <프로필> auth status openai-codex`)과 게이트웨이 보조 모델 설정을 확인한다. 인증 대기 중에는 현재 Codex 세션에서 일한 뒤 결과를 칸반에 기록할 수 있다. 기존 Python 샘플은 Claude를 사용한다.

## 업무 유형

| 의뢰 | 접수 자료 | 담당과 납품물 | 완료 기준 |
|---|---|---|---|
| Android 기능 기획 | 사용자 문제, 현재 화면, 현행 코드·제품 결정 | PM 기능 우선순위·구현안, 제작자 화면 문구·가이드, QA 검증표 | 변경 지점, 범위, 실패 조건, 승인할 결정의 출처를 확인 |
| 고객 문의 개선 | 개인정보를 제거한 문의 묶음, 승인된 FAQ | 고객 응대가 반복 문의와 답변 템플릿 정리, QA가 정책 및 재현 자료 검수 | 반복 유형의 근거 건수와 FAQ 수정안에 필요한 확인 항목 포함 |
| 제휴 미팅 준비 | 상대 회사, 협력 목표, 사용 가능한 제품 자료 | 마케팅이 제안 구성, 제작자가 소개 1장·데모 자료 제작, QA가 기능 주장 검수 | 상대가 검토할 제안, 예상 질문, 다음 단계 포함 |
| 스토어 페이지 개선 | 현재 등록정보, 실제 앱 캡처, 개선 목표 | 마케팅이 메시지 가설, 제작자가 첫 스크린샷 시안, QA가 실화면과 대조 | 기준안과 변경안을 구분하고 측정 지표와 비교 기간 명시 |

## 진행 중인 프로젝트를 활용한 예제

현재 프로젝트의 한 흐름을 읽기 전용으로 확인하고, 필요한 상황과 기대 결과를 [파비 예제](examples/pabi-connection/brief.md)처럼 작성한다. 저장소에 넣는 테스트 입력에는 검증에 필요한 가정만 남긴다. 내부 근거와 실행 기록은 Git에서 제외하는 `hermes/jobs/`에 둔다.

```bash
mkdir -p hermes/jobs/pabi-connection
cp -n hermes/examples/pabi-connection/brief.md hermes/jobs/pabi-connection/brief.md
bash hermes/submit_work.sh --example pabi-connection "파비 첫 연결과 첫 사용 · 팀 테스트"
hermes kanban --board odoc-test list
```

예제 카드는 수동 검토 대기(`blocked`)로 접수된다. `python3 -m unittest discover -s hermes/tests -v`는 실제 Hermes와 모델을 호출하지 않고 보드 선택, 안전한 대기 상태, 중복 방지 키와 잘못된 입력 처리를 검사한다.
