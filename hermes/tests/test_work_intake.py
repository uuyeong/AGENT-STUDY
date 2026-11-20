import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from textwrap import dedent
import unittest


HERMES_DIR = Path(__file__).resolve().parents[1]


class WorkIntakeTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.command = self.root / "hermes" / "submit_work.sh"
        self.command.parent.mkdir()
        shutil.copy(HERMES_DIR / "submit_work.sh", self.command)
        self.job = self.command.parent / "jobs" / "pabi-connection"
        self.job.mkdir(parents=True)
        shutil.copy(
            HERMES_DIR / "examples" / "pabi-connection" / "brief.md",
            self.job / "brief.md",
        )

        fake_cli = self.root / "bin" / "hermes"
        fake_cli.parent.mkdir()
        fake_cli.write_text(
            "#!/usr/bin/env python3\n" + dedent("""\
                import json
                import os
                import sys

                with open(os.environ["HERMES_TEST_LOG"], "a") as log:
                    log.write(json.dumps(sys.argv[1:]) + "\\n")
            """),
            encoding="utf-8",
        )
        fake_cli.chmod(0o755)
        self.log = self.root / "commands.jsonl"
        self.environment = {
            **os.environ,
            "PATH": os.pathsep.join((str(fake_cli.parent), os.environ["PATH"])),
            "HERMES_TEST_LOG": str(self.log),
        }

    def submit(self, *args):
        return subprocess.run(
            ["bash", str(self.command), *args],
            env=self.environment,
            text=True,
            capture_output=True,
        )

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_pabi_example_uses_test_board_and_a_stable_blocked_card(self):
        args = ("--example", "pabi-connection", "파비 연결·첫 사용 예제")
        for _ in range(2):
            result = self.submit(*args)
            self.assertEqual(result.returncode, 0, result.stderr)

        board, card, repeated_board, repeated_card = self.calls()
        self.assertEqual(board[:4], ["kanban", "boards", "create", "odoc-test"])
        self.assertEqual(card[:5], ["kanban", "--board", "odoc-test", "create", args[-1]])
        self.assertEqual(card[card.index("--initial-status") + 1], "blocked")
        self.assertEqual(card[card.index("--idempotency-key") + 1], "pabi-connection")
        self.assertEqual(card[card.index("--workspace") + 1], f"dir:{self.job}")
        self.assertNotIn("--triage", card)
        self.assertEqual((repeated_board, repeated_card), (board, card))

    def test_real_intake_uses_work_board_and_starts_blocked(self):
        result = self.submit("pabi-connection", "테스트 브리프 복사본으로 접수 검사")
        self.assertEqual(result.returncode, 0, result.stderr)
        board, card = self.calls()
        self.assertEqual(board[:4], ["kanban", "boards", "create", "odoc-work"])
        self.assertEqual(card[:4], ["kanban", "--board", "odoc-work", "create"])
        self.assertEqual(card[card.index("--initial-status") + 1], "blocked")

    def test_missing_brief_stops_before_hermes_call(self):
        result = self.submit("--example", "missing-brief", "예제")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.log.exists())

    def test_unsafe_job_id_stops_before_hermes_call(self):
        result = self.submit("--example", "../pabi-connection", "예제")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.log.exists())
