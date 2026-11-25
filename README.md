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
   파비 관련 자료 보낼게. 파비는 두 가지 사업으로 진행하고 있는데 서로 별개니까 섞지 말고 따로 봐줘. 첫째, 정부지원사업: 외국인 K-pop 팬에게 한국어를 가르치는 교육 콘텐츠로 지원사업에 등록하려고 해. 지원사업을 받으려면 무엇이 필요한지 먼저 파악하고, 그에 맞게 교육 콘텐츠 방향을 디벨롭해줘. 둘째, 아리랑TV와 협업하는 AI 굿즈 판매: 파비를 많이 팔고 싶어. 앱이나 파비 로봇에 추가하면 좋을 기능이 있는지, 셀링 포인트를 뭘로 잡고 어떻게 팔아야 하는지 알려줘.
   ```

2. `PM 질문`이 나오면 답을 입력합니다. Enter만 누르면 PM이 알아서 정합니다.
3. PM의 정리안이 나오면 `y`를 입력합니다. 고치고 싶은 점이 있으면 `y` 대신 말로 입력합니다.
4. 직원 작업과 검수가 끝날 때까지 기다립니다. 약 10분 걸립니다.

## 결과 보기

```bash
open hermes/jobs/pabi-demo/runs/*/delivery/README.md
```

PM 보고가 열립니다. 맨 위 "PM 정리"에서 PM이 어떻게 판단하고 누구에게 일을 맡겨 어떤 결론을 냈는지 먼저 보고, 이어서 질문별 답과 결과 문서를 볼 수 있습니다.

모델 인증 오류가 나면 아래 명령으로 상태를 확인합니다.

```bash
hermes -p default auth status openai-codex
```
