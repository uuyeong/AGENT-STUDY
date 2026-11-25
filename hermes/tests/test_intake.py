import copy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from intake import CONVERSATION, check_spec, load_sources, run_intake
from work_spec import JobError, load_job


SOURCE = "회의록.md"
SOURCE_TEXT = """# 3차 회의
- 출시일은 **3월 2일**로 확정했다.
- 가격은 12만~15만 원 사이에서 검토 중이다.
"""


class IntakeTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.temp = Path(temp.name)
        (self.temp / "sources").mkdir()
        (self.temp / "sources" / SOURCE).write_text(SOURCE_TEXT, encoding="utf-8")
        self.root = self.temp / "jobs" / "launch"
        self.sources = load_sources([self.temp / "sources"])
        self.spec = {
            "title": "출시 홍보",
            "brief": "다음 달 출시 홍보 글을 만든다.",
            "assumptions": ["독자는 일반 소비자로 정했다."],
            "tracks": [{"id": "launch", "label": "출시 홍보", "objective": "출시 기능을 알린다."}],
            "outputs": [
                {"id": "blog", "track": "launch", "audience": "소비자", "goal": "블로그 글",
                 "checks": ["가격을 확정된 것처럼 쓰지 않는다.", "출시일을 근거 ID와 함께 쓴다."]},
                {"id": "faq", "track": "launch", "audience": "상담원", "goal": "FAQ", "needs": ["blog"],
                 "columns": ["질문", "답변"], "checks": ["질문을 5개 이상 쓴다."]},
            ],
            "evidence": [
                {"id": "launch-date", "status": "decision", "source": SOURCE,
                 "quote": "출시일은 3월 2일로 확정했다.", "summary": "출시일은 3월 2일이다."},
                {"id": "price", "status": "open", "source": SOURCE,
                 "quote": "가격은 12만~15만 원 사이에서 검토 중이다.", "summary": "가격은 검토 중이다."},
                {"id": "no-price", "status": "decision", "source": CONVERSATION,
                 "quote": "가격은 빼줘", "summary": "사용자가 가격 언급을 제외하라고 했다."},
            ],
        }
        self.questions = ["독자는 누구인가요?"]
        self.specs = []
        self.reviews = []
        self.replies = []
        self.said = []
        self.calls = []

    def backend(self, role, stage, prompt, usage_path):
        self.calls.append((role, stage, prompt))
        usage_path.write_text(json.dumps({"provider": "openai-codex", "model": "gpt-6-sol", "api_calls": 1,
                                          "input_tokens": 10, "output_tokens": 5, "completed": True}))
        if stage == "clarify":
            return json.dumps({"questions": self.questions})
        if role == "qa":
            return json.dumps({"issues": self.reviews.pop(0) if self.reviews else []})
        return json.dumps(self.specs.pop(0) if self.specs else self.spec, ensure_ascii=False)

    def ask(self, prompt):
        if not self.replies:
            raise EOFError
        return self.replies.pop(0)

    def start(self, **options):
        return run_intake(self.root, "출시 홍보 글 써줘. 가격은 빼줘", self.sources, self.backend,
                          self.ask, self.said.append, **options)

    def stages(self):
        return [stage for _, stage, _ in self.calls]

    def test_owner_answers_and_approval_save_valid_request(self):
        self.replies = ["일반 소비자", "y"]
        self.assertTrue(self.start())
        job = load_job(self.root)
        self.assertEqual(list(job.outputs), ["blog", "faq"])
        evidence = tomllib.loads((self.root / "evidence.toml").read_text())["evidence"]
        self.assertEqual(evidence[0]["quote"], "출시일은 3월 2일로 확정했다.")
        self.assertIn("## 접수 시 PM 가정", (self.root / "brief.md").read_text())
        self.assertEqual(self.stages(), ["clarify", "spec-1", "review-spec-1"])
        spec_prompt = self.calls[1][2]
        self.assertIn("일반 소비자", spec_prompt)
        self.assertIn(SOURCE_TEXT.splitlines()[1], spec_prompt)
        self.assertIn("독자는 누구인가요?", "\n".join(self.said))
        conversation = json.loads(next(self.root.glob("intake/*/conversation.json")).read_text())
        self.assertEqual(conversation["status"], "approved")

    def test_nothing_is_saved_without_approval(self):
        self.replies = ["", "n"]
        self.assertFalse(self.start())
        self.assertFalse((self.root / "job.toml").exists())
        conversation = json.loads(next(self.root.glob("intake/*/conversation.json")).read_text())
        self.assertEqual(conversation["status"], "aborted")

    def test_invented_quote_is_sent_back_to_pm(self):
        bad = copy.deepcopy(self.spec)
        bad["evidence"][0]["quote"] = "출시일은 4월 1일로 확정했다."
        self.specs = [bad]
        self.assertTrue(self.start(questions=False, confirm=False))
        self.assertEqual(self.stages(), ["spec-1", "spec-2", "review-spec-2"])
        self.assertIn("launch-date의 quote를", self.calls[1][2])

    def test_repeated_invalid_draft_stops_before_saving(self):
        bad = copy.deepcopy(self.spec)
        bad["outputs"][1]["needs"] = ["missing"]
        self.specs = [bad, bad]
        with self.assertRaisesRegex(JobError, "선행"):
            self.start(questions=False, confirm=False)
        self.assertFalse((self.root / "job.toml").exists())

    def test_qa_issues_trigger_one_revision_then_show_remaining(self):
        self.reviews = [["price: 상태 확인"], ["price: 아직 확인"]]
        self.replies = ["y"]
        self.assertTrue(self.start(questions=False))
        self.assertEqual(self.stages(), ["spec-1", "review-spec-1", "spec-2", "review-spec-2"])
        self.assertIn("price: 상태 확인", self.calls[2][2])
        self.assertIn("! price: 아직 확인", self.said[-2])

    def test_owner_feedback_revises_and_becomes_quotable(self):
        revised = copy.deepcopy(self.spec)
        revised["evidence"].append({"id": "tone", "status": "decision", "source": CONVERSATION,
                                    "quote": "말투는 친근하게 해줘", "summary": "친근한 말투를 쓴다."})
        self.specs = [self.spec, revised]
        self.replies = ["말투는 친근하게 해줘", "y"]
        self.assertTrue(self.start(questions=False))
        self.assertIn("사용자 수정 요청: 말투는 친근하게 해줘", self.calls[2][2])
        self.assertIn("tone", load_job(self.root).evidence)

    def test_feedback_rounds_are_limited(self):
        self.replies = ["a", "b", "c", "d"]
        self.assertFalse(self.start(questions=False))
        self.assertIn("수정은 3회까지", self.said[-1])
        self.assertFalse((self.root / "job.toml").exists())

    def test_existing_request_is_not_overwritten(self):
        self.root.mkdir(parents=True)
        (self.root / "brief.md").write_text("기존")
        with self.assertRaisesRegex(JobError, "이미"):
            self.start(questions=False, confirm=False)
        self.assertEqual((self.root / "brief.md").read_text(), "기존")
        self.assertFalse(self.calls)

    def test_quote_must_come_from_named_source(self):
        sources = {CONVERSATION: "가격은 빼줘", **self.sources}
        check_spec(self.spec, sources)
        wrong = copy.deepcopy(self.spec)
        wrong["evidence"][2]["source"] = SOURCE
        with self.assertRaisesRegex(JobError, "no-price"):
            check_spec(wrong, sources)
        wrong["evidence"][2]["source"] = "없는-자료.md"
        with self.assertRaisesRegex(JobError, "source"):
            check_spec(wrong, sources)

    def test_evidence_ids_stay_out_of_titles_and_goals(self):
        tagged = copy.deepcopy(self.spec)
        tagged["outputs"][0]["goal"] = "블로그 글[launch-date]"
        with self.assertRaisesRegex(JobError, "근거 ID"):
            check_spec(tagged, {CONVERSATION: "가격은 빼줘", **self.sources})

    def test_special_characters_survive_toml(self):
        tricky = copy.deepcopy(self.spec)
        tricky["brief"] = 'say "hi" \\ path\n둘째 줄'
        tricky["outputs"][0]["checks"].append('따옴표 "포함" 기준')
        files = check_spec(tricky, {CONVERSATION: "가격은 빼줘", **self.sources})
        self.assertIn('따옴표 "포함" 기준', tomllib.loads(files["job.toml"])["outputs"][0]["checks"])

    def test_sources_must_be_text_files(self):
        (self.temp / "slides.pdf").write_bytes(b"%PDF")
        with self.assertRaisesRegex(JobError, ".md 또는 .txt"):
            load_sources([self.temp / "slides.pdf"])


if __name__ == "__main__":
    unittest.main()
