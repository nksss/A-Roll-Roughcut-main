"""Remembered export folder. No GUI."""

import base64
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import review_server


class RememberedFolder(unittest.TestCase):
    def test_missing_store_uses_the_run_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            fallback = Path(tmp)
            store = fallback / ".export-dir"
            self.assertEqual(review_server.remembered_export_dir(fallback, store), fallback)

    def test_saved_folder_is_the_next_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fallback = root / "run"
            chosen = root / "desk"
            fallback.mkdir()
            chosen.mkdir()
            store = root / ".export-dir"
            review_server.remember_export_dir(chosen, store)
            self.assertEqual(review_server.remembered_export_dir(fallback, store), chosen.resolve())

    def test_gone_folder_falls_back_to_the_run_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fallback = root / "run"
            fallback.mkdir()
            store = root / ".export-dir"
            store.write_text(str(root / "missing") + "\n", encoding="utf-8")
            self.assertEqual(review_server.remembered_export_dir(fallback, store), fallback)

    def test_basename_keeps_two_pieces_apart(self):
        run = Path("/work/codex多模型/runs/20260923-1618")
        self.assertEqual(
            review_server.export_basename(run, "fcpxml"),
            "codex多模型-20260923-1618.fcpxml",
        )
        self.assertEqual(
            review_server.export_basename(run, "srt"),
            "codex多模型-20260923-1618.srt",
        )

    def test_default_export_file_is_inside_the_run_directory(self):
        run = Path("/work/推荐口播/runs/2026-10-07")
        self.assertEqual(
            review_server.default_export_file(run, "srt"),
            (run / "推荐口播-2026-10-07.srt").resolve(),
        )
        self.assertEqual(
            review_server.default_export_file(run, "mp4"),
            (run / "推荐口播-2026-10-07.mp4").resolve(),
        )

    def test_audio_only_subtitles_use_declared_sequence_rate(self):
        self.assertEqual(
            review_server.fallback_subtitle_fps({"source": {"fps": 29.97}}),
            (30, 1),
        )
        self.assertEqual(review_server.fallback_subtitle_fps({"source": {}}), (25, 1))

    def test_windows_state_requests_browser_save_picker(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "推荐口播" / "runs" / "2026-10-07"
            run.mkdir(parents=True)
            with patch.object(review_server.sys, "platform", "win32"):
                state = review_server.build_state(run, None, None)
            self.assertTrue(state["browserSavePicker"])
            self.assertEqual(state["exportNames"]["srt"], "推荐口播-2026-10-07.srt")

    def test_cancel_does_not_change_the_remembered_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fallback = root / "run"
            fallback.mkdir()
            store = root / ".export-dir"

            def canceled(*_args, **_kwargs):
                return SimpleNamespace(returncode=1, stdout="", stderr="User canceled. (-128)")

            with self.assertRaises(review_server.ExportCanceled):
                review_server.choose_export_file(fallback, "片.srt", "导出字幕", store=store, run=canceled)
            self.assertFalse(store.exists())

    def test_renamed_file_is_kept_and_its_folder_is_remembered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fallback = root / "run"
            desk = root / "desk"
            fallback.mkdir()
            desk.mkdir()
            chosen = desk / "新名字.srt"
            store = root / ".export-dir"
            seen = {}

            def picked(cmd, **_kwargs):
                seen["cmd"] = cmd
                return SimpleNamespace(returncode=0, stdout=str(chosen) + "\n", stderr="")

            got = review_server.choose_export_file(fallback, "旧名字.srt", "导出字幕", store=store, run=picked)
            self.assertEqual(got, chosen.resolve())
            self.assertEqual(store.read_text(encoding="utf-8").strip(), str(desk.resolve()))
            if seen["cmd"][0] == "powershell.exe":
                script = base64.b64decode(seen["cmd"][4]).decode("utf-16le")
                self.assertIn("旧名字.srt", script)
            else:
                self.assertIn("旧名字.srt", seen["cmd"])
                self.assertIn("choose file name", seen["cmd"][2])

    def test_windows_save_dialog_keeps_selected_file_and_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fallback = root / "run"
            desk = root / "desk"
            fallback.mkdir()
            desk.mkdir()
            chosen = desk / "字幕.srt"
            store = root / ".export-dir"
            seen = {}

            def picked(cmd, **_kwargs):
                seen["cmd"] = cmd
                return SimpleNamespace(returncode=0, stdout=str(chosen) + "\n", stderr="")

            with patch.object(review_server.sys, "platform", "win32"):
                got = review_server.choose_export_file(
                    fallback, "roughcut.srt", "导出字幕", store=store, run=picked
                )
            self.assertEqual(got, chosen.resolve())
            self.assertEqual(store.read_text(encoding="utf-8").strip(), str(desk.resolve()))
            self.assertEqual(seen["cmd"][0], "powershell.exe")
            script = base64.b64decode(seen["cmd"][4]).decode("utf-16le")
            self.assertIn("SaveFileDialog", script)
            self.assertIn("$owner.TopMost = $true", script)
            self.assertIn("ShowDialog($owner)", script)
            self.assertIn("roughcut.srt", script)

    def test_windows_cancel_does_not_change_the_remembered_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fallback = root / "run"
            fallback.mkdir()
            store = root / ".export-dir"

            def canceled(*_args, **_kwargs):
                return SimpleNamespace(returncode=1, stdout="", stderr="")

            with patch.object(review_server.sys, "platform", "win32"):
                with self.assertRaises(review_server.ExportCanceled):
                    review_server.choose_export_file(
                        fallback, "片.srt", "导出字幕", store=store, run=canceled
                    )
            self.assertFalse(store.exists())


if __name__ == "__main__":
    unittest.main()
