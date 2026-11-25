#!/usr/bin/env python3
"""Turn an owner's rough request and raw materials into a reviewed team-work request.

The PM asks what the materials cannot answer, drafts the request files, and QA checks them.
Nothing is saved until the owner approves the summary.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from functools import partial
from tempfile import TemporaryDirectory, mkdtemp

from run_work import (DEFAULT_MODEL, HERMES_DIR, hermes_backend, prompt_for, read_json, record_usage,
                      require_keys, run_job, write_json)
from work_spec import JobError, load_job, slug, text, texts


CONVERSATION = "의뢰 대화"
SOURCE_SUFFIXES = (".md", ".txt")
SOURCE_LIMIT = 90_000
PROMPT_LIMIT = 200_000
MAX_QUESTIONS = 3
MAX_FEEDBACK_ROUNDS = 3
LIMITS = {"tracks": 4, "outputs": 8, "evidence": 40}
QUOTE_RANGE = (4, 300)
JOB_FILES = ("brief.md", "job.toml", "evidence.toml")
STATUS_LABELS = {"fact": "사실", "decision": "결정", "proposal": "제안", "open": "미정"}
SPEC_KEYS = ("title", "questions", "brief", "assumptions", "tracks", "outputs", "evidence")
OUTPUT_KEYS = {"id", "track", "audience", "goal", "question", "checks"}
OUTPUT_OPTIONAL = {"needs", "columns"}
EVIDENCE_KEYS = ("id", "status", "source", "quote", "summary")
MARKUP = re.compile(r"[*`|#>_]")
EVIDENCE_TAG = re.compile(r"\[[a-z0-9]+(?:-[a-z0-9]+)*\]")

CLARIFY = """사용자의 요청과 첨부 자료를 읽고 의뢰서를 만들기 전에 사용자에게 물을 질문을 고른다.
사용자가 이번 결과로 답을 얻고 싶은 질문이나 내릴 결정이 요청에 분명하지 않으면 그것부터 묻는다.
산출물의 종류, 독자, 범위를 정하는 데 결정적이면서 자료와 요청으로 답할 수 없는 것만 묻는다.
자료에서 찾을 수 있거나 PM이 합리적으로 가정할 수 있는 것은 묻지 않는다. 최대 세 개, 한 줄씩 쓴다.
물을 것이 없으면 빈 배열로 둔다. {"questions":["질문"]} JSON 객체만 출력한다.
"""

DRAFT = """사용자의 요청, 대화, 첨부 자료를 팀이 작성할 실무 의뢰서로 구체화한다. 아래 JSON 객체만 출력한다.
{"title":"의뢰 제목","questions":["사용자가 답을 얻고 싶은 질문"],"brief":"목표·제약·납품 용도를 담은 문단","assumptions":["사용자가 정하지 않아 PM이 정한 가정"],
 "tracks":[{"id":"track-id","label":"업무 범위 이름","objective":"트랙의 목표"}],
 "outputs":[{"id":"output-id","track":"track-id","audience":"독자","goal":"산출물 목적","question":"이 산출물이 답할 질문",
   "checks":["관찰 가능한 통과 기준"],"needs":["선행 output-id"],"columns":["필드명"]}],
 "evidence":[{"id":"evidence-id","status":"fact","source":"자료 이름","quote":"원문 그대로의 연속 구간","summary":"한 가지 내용"}]}
- questions는 사용자가 이번 결과로 답을 얻고 싶은 질문이다. 사용자의 말에 가깝게 1~5개 적는다. 결과는 이 질문에 답하기 위해 만든다.
- 산출물마다 question에 questions 중 하나를 그대로 적는다. 모든 질문에 답하는 산출물이 있어야 한다. 질문에 답하지 않는 산출물은 만들지 않는다.
- checks의 첫 항목은 "문서 첫 부분에서 질문에 대한 답과 추천을 제시한다"처럼 질문에 직접 답하게 한다.
- 트랙은 목표·독자·검증 기준이 다른 사업이나 업무 범위다. 성격이 다르면 나누고, 하나면 하나만 둔다. 최대 네 개.
- 산출물은 사용자가 요청했거나 요청 목적에 꼭 필요한 문서만 최대 여덟 개 둔다. 요청 범위를 넘으면 assumptions에 이유를 적는다.
- checks는 QA가 문서만 보고 판정할 수 있는 기준 2~4개다. 사용자가 말한 제약과 금지 사항은 해당 산출물 checks에 넣는다.
- checks는 제공된 자료와 대화로 충족할 수 있어야 한다. 자료에 없는 정보(공식 원문, 실측 결과 등)가 필요하면 그 정보를 요구하지 말고 "확인 필요로 표시하고 확인 방법을 적는다"처럼 쓴다.
- needs는 같은 트랙의 선행 산출물만 쓴다. columns는 항목별 계획이나 표가 필요한 산출물에만 쓴다. 필요 없으면 키를 생략한다.
- ID는 소문자 영문·숫자·하이픈만 쓴다. 제목, brief, 가정, 트랙, 산출물에는 [근거-ID]를 붙이지 않는다.
- evidence는 작성에 쓸 근거를 최대 40개 뽑고, 근거마다 한 가지 내용만 담는다.
- source는 sources의 키 중 하나다. 사용자가 대화에서 한 말은 "의뢰 대화"를 쓴다.
- quote는 해당 자료에서 그대로 복사한 연속 구간 4~300자다. 생략·요약·번역·서식 변경을 하지 않는다. 실행기가 원문과 대조한다.
- status는 자료가 확인한 사실 fact, 사용자나 팀이 정한 사항 decision, 아이디어·가설·후보 proposal, 미정·확인 필요 open이다. 확정되지 않은 내용을 fact나 decision으로 올리지 않는다.
- summary는 quote의 범위를 넘는 내용을 덧붙이지 않는다. 날짜·수치·조건은 원문대로 쓴다.
- feedback이 있으면 previous_spec에서 지적된 부분만 고치고 나머지는 유지한다.
"""

REVIEW = """PM이 사용자의 요청을 구체화한 의뢰서를 작성 전에 검수한다. 인용문이 원문에 있는지는 실행기가 이미 확인했다.
- 각 근거의 summary가 quote를 벗어나거나 부풀리지 않는지, status가 quote의 확정 정도와 맞는지 본다.
- questions가 사용자가 실제로 알고 싶은 것을 담았는지, 각 산출물이 질문에 직접 답하도록 설계됐는지 본다.
- 산출물이 사용자의 요청과 답변을 빠짐없이 다루는지, 요청하지 않은 범위를 가정 없이 추가하지 않았는지 본다.
- checks가 문서만으로 판정 가능한지, 사용자가 말한 제약이 반영됐는지 본다.
- checks가 evidence에 없는 정보를 요구해 작성자가 충족할 수 없는지 본다.
- 서로 다른 사업이나 독자가 한 트랙에 섞였는지 본다.
작성을 막는 문제만 "ID: 고칠 점" 형식으로 적는다. 문제가 없으면 빈 배열로 둔다.
{"issues":["ID: 고칠 점"]} JSON 객체만 출력한다.
"""


def normalize(value):
    return " ".join(MARKUP.sub("", value).split())


def load_sources(paths):
    files = []
    for path in map(Path, paths):
        if path.is_dir() and not path.is_symlink():
            files.extend(sorted(item for item in path.iterdir() if item.suffix in SOURCE_SUFFIXES))
        else:
            files.append(path)
    sources = {}
    for path in files:
        if path.is_symlink() or not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            raise JobError(f"자료는 .md 또는 .txt 일반 파일이어야 합니다. {path}")
        if path.name in sources or path.name == CONVERSATION:
            raise JobError(f"자료 파일 이름이 중복됐습니다. {path.name}")
        try:
            sources[path.name] = text(path.read_text(encoding="utf-8"), path.name)
        except (OSError, UnicodeError) as error:
            raise JobError(f"자료를 읽을 수 없습니다. {path}") from error
    if sum(len(value.encode("utf-8")) for value in sources.values()) > SOURCE_LIMIT:
        raise JobError(f"자료가 {SOURCE_LIMIT:,}바이트를 넘습니다. 관련 자료만 골라 주세요.")
    return sources


def toml_value(value, where):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        if not value:
            return "[]"
        return "[\n" + "".join(f"  {json.dumps(item, ensure_ascii=False)},\n" for item in value) + "]"
    raise JobError(f"{where}에는 문자열 또는 문자열 배열을 넣으세요.")


def toml_tables(name, rows, keys):
    blocks = []
    for row in rows:
        lines = [f"[[{name}]]"]
        lines.extend(f"{key} = {toml_value(row[key], f'{name}.{key}')}" for key in keys if key in row)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def render_files(spec):
    title = text(spec["title"], "제목")
    if len(title.splitlines()) != 1:
        raise JobError("제목은 한 줄로 쓰세요.")
    brief = [f"# {title}", "", "## 알고 싶은 질문", "", *(f"- {item}" for item in texts(spec["questions"], "질문")), "",
             text(spec["brief"], "brief"), ""]
    assumptions = texts(spec["assumptions"], "가정")
    if assumptions:
        brief.extend(["## 접수 시 PM 가정", "", *(f"- {item}" for item in assumptions), ""])
    job = (f"title = {toml_value(title, 'title')}\n"
           f"questions = {toml_value(list(spec['questions']), 'questions')}\n\n"
           + toml_tables("tracks", spec["tracks"], ("id", "label", "objective")) + "\n"
           + toml_tables("outputs", spec["outputs"], ("id", "track", "question", "audience", "goal", "needs", "columns", "checks")))
    return {
        "brief.md": "\n".join(brief),
        "job.toml": job,
        "evidence.toml": toml_tables("evidence", spec["evidence"], EVIDENCE_KEYS),
    }


def check_spec(spec, sources):
    """Validate a PM draft in code and return the request files it produces."""
    require_keys(spec, SPEC_KEYS, "의뢰 구체화")
    for key, limit in LIMITS.items():
        rows = spec[key]
        if not isinstance(rows, list) or not 1 <= len(rows) <= limit or any(not isinstance(row, dict) for row in rows):
            raise JobError(f"{key}에는 1~{limit}개의 항목이 필요합니다.")
    for row in spec["tracks"]:
        require_keys(row, ("id", "label", "objective"), "트랙")
    questions = texts(spec["questions"], "질문")
    if not 1 <= len(questions) <= 5 or any(len(item.splitlines()) != 1 for item in questions):
        raise JobError("questions에는 한 줄 질문 1~5개가 필요합니다.")
    plain = [spec["title"], spec["brief"], *spec["assumptions"], *questions,
             *(row[key] for row in spec["tracks"] for key in ("label", "objective")),
             *(row.get(key) for row in spec["outputs"] for key in ("audience", "goal")),
             *(check for row in spec["outputs"] for check in row.get("checks", []))]
    for value in plain:
        if isinstance(value, str) and EVIDENCE_TAG.search(value):
            raise JobError(f"근거 ID는 evidence에만 씁니다. 제목·목적·기준에서 빼세요. {value[:40]}")
    for row in spec["outputs"]:
        if not OUTPUT_KEYS <= row.keys() <= OUTPUT_KEYS | OUTPUT_OPTIONAL:
            raise JobError(f"산출물 항목을 확인하세요. {row.get('id')}")
    for row in spec["evidence"]:
        require_keys(row, EVIDENCE_KEYS, "근거")
        key = slug(row["id"], "근거 ID")
        source = text(row["source"], f"{key}.source")
        if source not in sources:
            raise JobError(f"{key}의 source는 제공된 자료 이름이어야 합니다. {source}")
        quote = normalize(text(row["quote"], f"{key}.quote"))
        if not QUOTE_RANGE[0] <= len(quote) <= QUOTE_RANGE[1]:
            raise JobError(f"{key}의 quote는 {QUOTE_RANGE[0]}~{QUOTE_RANGE[1]}자여야 합니다.")
        if quote not in normalize(sources[source]):
            raise JobError(f"{key}의 quote를 {source} 원문에서 찾을 수 없습니다. 원문을 그대로 복사하세요.")
    files = render_files(spec)
    with TemporaryDirectory() as temp:
        for name, content in files.items():
            (Path(temp) / name).write_text(content, encoding="utf-8")
        load_job(temp)
    return files


def summarize(spec, issues):
    lines = [f"# {spec['title']}", "", "알고 싶은 질문", *(f"  - {item}" for item in spec["questions"]), "",
             spec["brief"], ""]
    if spec["assumptions"]:
        lines.extend(["PM 가정", *(f"  - {item}" for item in spec["assumptions"]), ""])
    for track in spec["tracks"]:
        lines.append(f"[{track['label']}] {track['objective']}")
        for output in spec["outputs"]:
            if output["track"] == track["id"]:
                after = f" · 선행 {', '.join(output['needs'])}" if output.get("needs") else ""
                lines.append(f"  - {output['id']}: {output['goal']} (독자: {output['audience']}{after})")
                lines.append(f"      답할 질문: {output['question']}")
                lines.extend(f"      · {check}" for check in output["checks"])
        lines.append("")
    counts = {}
    for row in spec["evidence"]:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    by_status = " · ".join(f"{label} {counts[key]}" for key, label in STATUS_LABELS.items() if key in counts)
    sources = sorted({row["source"] for row in spec["evidence"]})
    lines.extend([f"근거 {len(spec['evidence'])}개 ({by_status}) · 출처 {', '.join(sources)}", ""])
    if issues:
        lines.extend(["QA 미해결 의견", *(f"  ! {item}" for item in issues), ""])
    return "\n".join(lines)


class Intake:
    def __init__(self, request, sources, invoke, record):
        self.turns = [{"from": "owner", "text": request}]
        self.sources = sources
        self.invoke = invoke
        self.record = record
        self.round = 0

    def owner_says(self, words):
        self.turns.append({"from": "owner", "text": words})

    def all_sources(self):
        owner = "\n".join(turn["text"] for turn in self.turns if turn["from"] == "owner")
        return {CONVERSATION: owner, **self.sources}

    def clarify(self):
        answer = self.invoke("pm", "clarify", CLARIFY, {"conversation": self.turns, "sources": self.sources})
        data = read_json(answer, "PM 질문")
        require_keys(data, ("questions",), "PM 질문")
        questions = texts(data["questions"], "PM 질문")
        if len(questions) > MAX_QUESTIONS or any(len(item.splitlines()) != 1 for item in questions):
            raise JobError(f"PM 질문은 한 줄씩 최대 {MAX_QUESTIONS}개여야 합니다.")
        return questions

    def draft(self, feedback=None, previous=None):
        self.round += 1
        data = {"conversation": self.turns, "sources": self.all_sources()}
        if feedback:
            data["feedback"] = feedback
            data["previous_spec"] = previous
        spec = read_json(self.invoke("pm", f"spec-{self.round}", DRAFT, data), "PM 의뢰 구체화")
        self.record(f"spec-{self.round}.json", spec)
        return spec

    def checked_draft(self, feedback=None, previous=None):
        """Draft once more with the validator's message if code checks reject the first try."""
        spec = self.draft(feedback, previous)
        try:
            return spec, check_spec(spec, self.all_sources())
        except JobError as error:
            spec = self.draft([*(feedback or []), f"실행기 검증 오류: {error}"], spec)
            return spec, check_spec(spec, self.all_sources())

    def review(self, spec):
        data = {"conversation": self.turns, "spec": spec}
        result = read_json(self.invoke("qa", f"review-spec-{self.round}", REVIEW, data), "QA 의뢰 검수")
        require_keys(result, ("issues",), "QA 의뢰 검수")
        issues = list(texts(result["issues"], "QA 의뢰 검수"))
        self.record(f"review-spec-{self.round}.json", {"issues": issues})
        return issues

    def propose(self, feedback=None, previous=None):
        spec, files = self.checked_draft(feedback, previous)
        issues = self.review(spec)
        if issues:
            spec, files = self.checked_draft(issues, spec)
            issues = self.review(spec)
        return spec, files, issues


def run_intake(root, request, sources, backend, ask, say, questions=True, confirm=True):
    """Hold the owner conversation and save the approved request files. Returns True when saved."""
    if any((root / name).exists() for name in JOB_FILES):
        raise JobError(f"{root.name}에 이미 의뢰서가 있습니다. 다른 의뢰 ID를 사용하세요.")
    (root / "intake").mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = Path(mkdtemp(prefix=f"{timestamp}-", dir=root / "intake"))
    (session / "usage").mkdir()
    stages = {}

    def invoke(role, stage, instructions, data):
        stages[f"{role}-{stage}"] = role
        print(f"[접수] {stage} ({role})", file=sys.stderr, flush=True)
        return backend(role, stage, prompt_for(role, instructions, data), session / "usage" / f"{role}-{stage}.json")

    def record(name, data):
        write_json(session / name, data)

    def listen(prompt):
        try:
            return ask(prompt).strip()
        except EOFError:
            raise JobError("입력이 끝나 접수를 중단했습니다.") from None

    intake = Intake(request, sources, invoke, record)
    status = "failed"
    try:
        if questions:
            for number, question in enumerate(intake.clarify(), 1):
                intake.turns.append({"from": "pm", "text": question})
                say(f"PM 질문 {number}. {question}")
                answer = listen("> ")
                intake.owner_says(answer or "(답변 없음. PM이 판단)")
        spec, files, issues = intake.propose()
        for feedback_round in range(MAX_FEEDBACK_ROUNDS + 1):
            say(summarize(spec, issues))
            if not confirm:
                break
            reply = ""
            while not reply:
                reply = listen("진행하려면 y, 중단하려면 n, 고칠 점이 있으면 그대로 입력하세요: ")
            if reply.lower() in {"y", "yes", "네", "응", "진행"}:
                break
            if reply.lower() in {"n", "no", "중단"} or feedback_round == MAX_FEEDBACK_ROUNDS:
                status = "aborted"
                limit = "" if reply.lower() in {"n", "no", "중단"} else f"수정은 {MAX_FEEDBACK_ROUNDS}회까지입니다. "
                say(f"{limit}의뢰서를 저장하지 않았습니다.")
                return False
            intake.owner_says(reply)
            spec, files, issues = intake.propose([f"사용자 수정 요청: {reply}"], spec)
        for name, content in files.items():
            (root / name).write_text(content, encoding="utf-8")
        status = "approved"
        say(f"의뢰서를 저장했습니다. {root}")
        return True
    finally:
        record("conversation.json", {"turns": intake.turns, "status": status})
        record("usage-summary.json", record_usage(session, stages))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("job_id", help="hermes/jobs 아래에 만들 의뢰 ID")
    parser.add_argument("-m", "--message", help="요청 내용. 생략하면 입력을 받습니다.")
    parser.add_argument("-s", "--source", action="append", default=[], help="첨부 자료 파일 또는 폴더 (.md, .txt)")
    parser.add_argument("--skip-questions", action="store_true", help="PM 질문 없이 가정으로 진행")
    parser.add_argument("--yes", action="store_true", help="요약 확인 없이 저장")
    parser.add_argument("--run", action="store_true", help="저장 후 바로 팀 작업 실행")
    parser.add_argument("--profile", default="default", help="Hermes 인증 프로필")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI Codex 모델 ID")
    parser.add_argument("--timeout", type=int, default=300, help="호출당 최대 대기 시간(초)")
    args = parser.parse_args()
    try:
        job_id = slug(args.job_id, "의뢰 ID")
        jobs = HERMES_DIR / "jobs"
        if jobs.is_symlink() or (jobs / job_id).is_symlink():
            raise JobError("hermes/jobs와 의뢰 폴더는 일반 디렉터리여야 합니다.")
        if not re.fullmatch(r"gpt-[a-z0-9][a-z0-9.-]*", args.model) or args.timeout < 1:
            raise JobError("Codex 모델 ID와 양수 대기 시간을 지정하세요.")
        sources = load_sources(args.source)
        request = args.message or input("PM에게 요청할 내용을 입력하세요: ")
        request = text(request, "요청")
        root = jobs / job_id
        backend = hermes_backend(args.profile, args.model, args.timeout, PROMPT_LIMIT)
        saved = run_intake(root, request, sources, backend, input, partial(print, flush=True),
                           questions=not args.skip_questions, confirm=not args.yes)
        if saved and args.run:
            run = run_job(load_job(root), hermes_backend(args.profile, args.model, args.timeout))
            print(run / "delivery" / "README.md")
        elif saved:
            print(f"팀 작업 실행: python3 hermes/run_work.py {job_id}")
    except (JobError, OSError) as error:
        parser.exit(2, f"{error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "\n중단했습니다.\n")


if __name__ == "__main__":
    main()
