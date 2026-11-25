# AGENT-STUDY

PM에게 말로 요청하면 PM이 직원을 배정하고, 검수를 통과한 문서를 돌려주는 AI 팀입니다.

[설계](docs/DESIGN.md) · [파비 시연 결과](docs/RESULTS.md)

## 시연

터미널에서 순서대로 실행합니다.

```bash
cd ~/Developer/AGENT-STUDY
```

이전 시연 기록을 지웁니다. 처음이면 건너뛰어도 됩니다.

```bash
rm -rf hermes/jobs/pabi-demo
```

PM을 부르고 파비 자료를 넘깁니다.

```bash
python3 hermes/intake.py pabi-demo -s docs/cases/pabi/inputs --run
```

## 터미널에 입력할 것

1. `PM에게 요청할 내용을 입력하세요:`가 나오면 아래 문장을 붙여넣고 Enter를 누릅니다.

   ```text
   파비 관련 자료 보낼게. 지금 두 가지 사업을 보고 있어. 하나는 정부지원사업에 낼 K-pop 한국어 교육 콘텐츠고, 하나는 아리랑TV랑 협업해서 파는 AI 굿즈야. 둘은 별개 사업이니까 섞지 말고, 각각 내부 검토용으로 뭘 만들어야 할지 정리해서 작업해줘.
   ```

2. `PM 질문`이 나오면 답을 입력합니다. Enter만 누르면 PM이 알아서 정합니다.
3. PM의 정리안이 나오면 `y`를 입력합니다. 고치고 싶은 점이 있으면 `y` 대신 말로 입력합니다.
4. 직원 작업과 검수가 끝날 때까지 기다립니다. 약 10분 걸립니다.

## 결과 보기

```bash
open hermes/jobs/pabi-demo/runs/*/delivery/README.md
```

PM 보고가 열립니다. 결과 문서는 같은 폴더에 있습니다.

모델 인증 오류가 나면 아래 명령으로 상태를 확인합니다.

```bash
hermes -p default auth status openai-codex
```
