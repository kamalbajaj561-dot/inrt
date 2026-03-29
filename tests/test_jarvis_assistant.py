import pathlib
import tempfile
import unittest

from jarvis_assistant import JarvisAssistant


class JarvisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.assistant = JarvisAssistant(workspace_root=self.root, voice_enabled=False)
        self.assistant.confirm_required = False

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_wake_word_required(self) -> None:
        result = self.assistant.handle_command("run tests")
        self.assertFalse(result.ok)
        self.assertIn("Wake word", result.message)

    def test_ask_question_works_without_model_key(self) -> None:
        result = self.assistant.handle_command("jarvis ask how do i debug a traceback")
        self.assertTrue(result.ok)
        self.assertIn("Debug plan", result.message)

    def test_workspace_escape_blocked(self) -> None:
        result = self.assistant.write_file("../escape.txt", "nope")
        self.assertFalse(result.ok)
        self.assertIn("Path escapes", result.message)


if __name__ == "__main__":
    unittest.main()
