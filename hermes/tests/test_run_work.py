import json
from pathlib import Path
from subprocess import CompletedProcess
import sys
from tempfile import TemporaryDirectory
from textwrap import dedent
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_work import JobError, hermes_backend, load_job, run_job


class WorkRunTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        (self.root / "brief.md").write_text("두 팀의 자료로 내부 의사결정을 준비한다.")
        (self.root / "job.toml").write_text(dedent("""\
            title = "팀 개선"
            [[tracks]]
            id = "service"
            label = "고객지원"
            objective = "문의 처리 개선"
            [[tracks]]
            id = "ops"
            label = "운영"
            objective = "점검 개선"
            [[outputs]]
            id = "faq"
            track = "service"
            audience = "CS"
            goal = "FAQ"
            checks = ["실행 징후"]
            [[outputs]]
            id = "scripts"
            track = "service"
            audience = "CS"
            goal = "응대 문구"
            checks = ["일관성"]
            needs = ["faq"]
            [[outputs]]
            id = "checks"
            track = "ops"
            audience = "운영팀"
            goal = "점검 시트"
            checks = ["담당"]
            columns = ["item", "owner"]
            """))
        evidence = [
            ("ticket", "proposal", "service-evidence-marker"),
            ("audit", "fact", "ops-evidence-marker"),
            ("unknown", "open", "unassigned-marker"),
        ]
        (self.root / "evidence.toml").write_text("".join(
            f'[[evidence]]\nid = "{key}"\nstatus = "{status}"\nsource = "가공 기록"\nsummary = "{summary}"\n'
            for key, status, summary in evidence
        ))
        self.plan = {
            "routing": {
                "ticket": {"tracks": ["service"], "reason": "문의 자료"},
                "audit": {"tracks": ["ops"], "reason": "점검 자료"},
                "unknown": {"tracks": [], "reason": "검토 대기"},
            },
            "assignments": {
                "faq": {"role": "client", "format": "md", "focus": "반복 문의"},
                "scripts": {"role": "producer", "format": "md", "focus": "고객 문구"},
                "checks": {"role": "product", "format": "csv", "focus": "현장 확인"},
            },
        }
        self.calls = []
        self.reviews = []
        self.routing_reviews = []
        self.duplicate_review = False
        self.bad_csv = False

    def invoke(self, role, stage, prompt, usage_path):
        self.calls.append((role, stage, prompt))
        if stage in {"plan", "replan"}:
            return json.dumps(self.plan)
        if stage.startswith("review-routing-"):
            issues = self.routing_reviews.pop(0) if self.routing_reviews else []
            return json.dumps({"routing_issues": issues})
        if stage.startswith("review-"):
            _, round_number, track = stage.split("-")
            index = int(round_number) - 1
            issues = self.reviews[index] if index < len(self.reviews) else {}
            keys = ("faq", "scripts") if track == "service" else ("checks",)
            if self.duplicate_review and track == "service":
                return '{"outputs":{"faq":["검수 차단"],"faq":[],"scripts":[]}}'
            return json.dumps({"outputs": {key: issues.get(key, []) for key in keys}})
        if "checks-" in stage:
            return "mistake\n" if self.bad_csv else "item,owner\n재고,운영\n"
        return f"# 작업 결과\n\n{stage}"

    def test_routes_evidence_and_delivers_markdown_and_csv(self):
        self.plan["assignments"]["faq"]["focus"] = "ops-evidence-marker"
        run = run_job(load_job(self.root), self.invoke)
        files = {p.name for p in (run / "delivery").iterdir()}
        self.assertEqual(files, {"README.md", "faq.md", "scripts.md", "checks.csv"})
        drafts = {stage: prompt for _, stage, prompt in self.calls if stage.endswith("-draft")}
        self.assertIn("service-evidence-marker", drafts["faq-draft"])
        self.assertNotIn("ops-evidence-marker", drafts["faq-draft"])
        self.assertNotIn("unassigned-marker", drafts["faq-draft"])
        self.assertIn("faq-draft", drafts["scripts-draft"])
        self.assertNotIn("service-evidence-marker", drafts["checks-draft"])
        reviews = {stage: prompt for _, stage, prompt in self.calls if stage.startswith("review-1-")}
        self.assertNotIn("ops-evidence-marker", reviews["review-1-service"])
        self.assertNotIn("service-evidence-marker", reviews["review-1-ops"])

    def test_revises_dependent_output_and_rechecks(self):
        self.reviews = [{"faq": ["출처 필요"]}, {}]
        run = run_job(load_job(self.root), self.invoke)
        calls = {stage: prompt for _, stage, prompt in self.calls}
        self.assertIn("출처 필요", calls["faq-revision"])
        self.assertIn("faq-revision", calls["scripts-revision"])
        self.assertNotIn("checks-revision", calls)
        self.assertIn("review-2-service", calls)
        self.assertTrue((run / "delivery" / "scripts.md").exists())

    def test_failed_review_never_releases_files(self):
        self.reviews = [{"faq": ["출처 필요"]}, {"faq": ["근거 부족"]}, {"faq": ["근거 부족"]}]
        with self.assertRaisesRegex(JobError, "검수"):
            run_job(load_job(self.root), self.invoke)
        self.assertEqual(list(self.root.glob("runs/*/delivery")), [])

    def test_second_revision_uses_latest_feedback_without_overwriting_first(self):
        self.reviews = [{"faq": ["출처 필요"]}, {"faq": ["원인 미확인"]}, {}]
        run = run_job(load_job(self.root), self.invoke)
        calls = {stage: prompt for _, stage, prompt in self.calls}
        self.assertIn("원인 미확인", calls["faq-revision-2"])
        self.assertIn("faq-revision-2", calls["scripts-revision-2"])
        self.assertTrue((run / "drafts" / "faq-revision.md").is_file())
        self.assertTrue((run / "drafts" / "faq-revision-2.md").is_file())
        self.assertTrue((run / "review-3.json").is_file())

    def test_no_cross_track_dependency(self):
        path = self.root / "job.toml"
        path.write_text(path.read_text().replace('needs = ["faq"]', 'needs = ["checks"]'))
        with self.assertRaisesRegex(JobError, "트랙"):
            load_job(self.root)
        self.assertFalse(self.calls)

    def test_bad_csv_is_rejected_before_review(self):
        self.bad_csv = True
        with self.assertRaisesRegex(JobError, "CSV"):
            run_job(load_job(self.root), self.invoke)
        self.assertFalse(any(stage.startswith("review-1-") for _, stage, _ in self.calls))
        self.assertEqual(list(self.root.glob("runs/*/delivery")), [])

    def test_unknown_routing_track_is_rejected_before_drafts(self):
        self.plan["routing"]["ticket"]["tracks"] = ["missing"]
        with self.assertRaisesRegex(JobError, "트랙"):
            run_job(load_job(self.root), self.invoke)
        self.assertEqual([stage for _, stage, _ in self.calls], ["plan"])

    def test_routes_are_rechecked_before_specialist_calls(self):
        self.routing_reviews = [["ticket 귀속 재검토"], ["아직 오류"]]
        with self.assertRaisesRegex(JobError, "분류"):
            run_job(load_job(self.root), self.invoke)
        self.assertEqual([stage for _, stage, _ in self.calls],
                         ["plan", "review-routing-1", "replan", "review-routing-2"])

    def test_successful_routing_repair_delivers_a_separate_run(self):
        self.routing_reviews = [["ticket 귀속 재검토"], []]
        run = run_job(load_job(self.root), self.invoke)
        self.assertTrue((run / "replan.json").is_file())
        self.assertTrue((run / "delivery" / "faq.md").is_file())
        self.routing_reviews = [["ticket 귀속 재검토"], ["아직 오류"]]
        with self.assertRaises(JobError):
            run_job(load_job(self.root), self.invoke)
        self.assertEqual(list(self.root.glob("runs/*/delivery")), [run / "delivery"])

    def test_rejects_duplicate_review_keys(self):
        self.duplicate_review = True
        with self.assertRaisesRegex(JobError, "중복"):
            run_job(load_job(self.root), self.invoke)
        self.assertEqual(list(self.root.glob("runs/*/delivery")), [])

    def test_rejects_whitespace_in_routed_track_id(self):
        self.plan["routing"]["ticket"]["tracks"] = [" service "]
        with self.assertRaisesRegex(JobError, "트랙"):
            run_job(load_job(self.root), self.invoke)

    def test_hermes_backend_requires_a_completed_codex_usage_record(self):
        usage_path = self.root / "usage.json"
        run_model = hermes_backend("default", "gpt-6-sol", 30)

        def fake_hermes(command, **kwargs):
            self.assertIn("--safe-mode", command)
            self.assertEqual(command[command.index("--toolsets") + 1], "")
            self.assertEqual(command[command.index("--provider") + 1], "openai-codex")
            self.assertEqual(kwargs["cwd"], self.root)
            usage_path.write_text(json.dumps({
                "provider": provider, "model": "gpt-6-sol",
                "completed": True, "api_calls": 1, "failed": False,
            }))
            return CompletedProcess(command, 0, "# 작업 결과", "")

        with patch("run_work.subprocess.run", side_effect=fake_hermes):
            provider = "openai-codex"
            self.assertEqual(run_model("pm", "plan", "payload", usage_path), "# 작업 결과")
            provider = "anthropic"
            with self.assertRaisesRegex(JobError, "OpenAI Codex"):
                run_model("pm", "plan", "payload", usage_path)


if __name__ == "__main__":
    unittest.main()
