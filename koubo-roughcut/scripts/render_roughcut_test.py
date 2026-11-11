"""Constant-frame-rate rough cut uses the same grid as the XML. No ffmpeg."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import render_roughcut


class ConstantRate(unittest.TestCase):
    def test_hardware_encoder_detection_reads_ffmpeg_encoder_list(self):
        result = type(
            "Result",
            (),
            {
                "stdout": (
                    " V....D h264_nvenc NVIDIA NVENC H.264\n"
                    " V..... libx264 software H.264\n"
                    " V....D hevc_amf AMD AMF HEVC\n"
                )
            },
        )()
        with patch.object(render_roughcut.subprocess, "run", return_value=result):
            self.assertEqual(render_roughcut.available_h264_encoders(), {"h264_nvenc"})
        self.assertEqual(
            render_roughcut.encoder_attempt_order({"h264_nvenc", "h264_qsv"}),
            ["h264_nvenc", "h264_qsv", None],
        )
        self.assertEqual(render_roughcut.encoder_attempt_order(set()), [None])

    def test_video_encoder_arguments_preserve_cpu_fallback(self):
        self.assertEqual(
            render_roughcut.video_encoder_args("h264_nvenc"),
            ["-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "18", "-b:v", "0"],
        )
        self.assertEqual(
            render_roughcut.video_encoder_args(None),
            ["-c:v", "libx264", "-preset", "fast", "-crf", "18"],
        )
        vaapi = next(item for item in render_roughcut.GPU_ENCODERS if item[0] == "h264_vaapi")
        self.assertEqual(vaapi[2], ["-vaapi_device", "/dev/dri/renderD128"])
        self.assertEqual(vaapi[3], ["-vf", "format=nv12,hwupload"])

    def test_failed_hardware_encode_retries_with_software_encoder(self):
        class FakeProcess:
            def __init__(self, code, stderr):
                self.stdout = io.StringIO("out_time=00:00:00.040000\nprogress=continue\n")
                self.stderr = io.StringIO(stderr)
                self.code = code

            def poll(self):
                return self.code

            def wait(self):
                return self.code

            def kill(self):
                self.code = -9

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.mp4"
            source.touch()
            output = Path(tmp) / "roughcut.mp4"
            calls = []

            def fake_popen(cmd, **_kwargs):
                calls.append(cmd)
                if len(calls) == 1:
                    return FakeProcess(1, "Cannot load GPU driver")
                return FakeProcess(0, "")

            with (
                patch.object(render_roughcut, "probe", return_value={"fps_n": 25, "fps_d": 1, "has_audio": False}),
                patch.object(render_roughcut, "filter_graph", return_value="[0:v]null[outv]"),
                patch.object(render_roughcut, "available_h264_encoders", return_value={"h264_nvenc"}),
                patch.object(render_roughcut.subprocess, "Popen", side_effect=fake_popen),
            ):
                render_roughcut.render_mp4(
                    source,
                    {"keep": [{"sourceStart": 0, "sourceEnd": 1}]},
                    output,
                )

            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][calls[0].index("-c:v") + 1], "h264_nvenc")
            self.assertEqual(calls[1][calls[1].index("-c:v") + 1], "libx264")

    def test_loudness_target_is_validated_and_added_to_audio_graph(self):
        graph = render_roughcut.filter_graph([(0.0, 1.0, 25)], 25, True, target_lufs=-14)
        self.assertIn("loudnorm=I=-14.000:TP=-2:LRA=11", graph)
        self.assertEqual(render_roughcut.normalize_target_lufs("-14"), -14.0)
        with self.assertRaises(ValueError):
            render_roughcut.normalize_target_lufs(-0.5)
        with self.assertRaises(ValueError):
            render_roughcut.normalize_target_lufs("not-a-number")

    def test_audio_filter_can_be_disabled(self):
        graph = render_roughcut.filter_graph([(0.0, 1.0, 25)], 25, True, target_lufs=None)
        self.assertNotIn("loudnorm", graph)

    def test_video_without_audio_does_not_add_loudnorm(self):
        graph = render_roughcut.filter_graph([(0.0, 1.0, 25)], 25, False, target_lufs=-14)
        self.assertNotIn("loudnorm", graph)

    def test_bounds_match_the_xml_grid(self):
        keep = [
            {"sourceStart": 1.02, "sourceEnd": 1.40},
            {"sourceStart": 3.00, "sourceEnd": 3.50},
        ]
        bounds = render_roughcut.segment_bounds(keep, 25, 1)
        self.assertEqual(bounds[0], (1.04, 1.4, 9))
        self.assertEqual(bounds[1], (3.0, 3.52, 13))

    def test_each_piece_is_locked_to_the_subtitle_frame_count(self):
        graph = render_roughcut.filter_graph([(1.04, 1.40, 9), (3.0, 3.52, 13)], 25, True)
        self.assertIn("fps=25:eof_action=pass", graph)
        self.assertIn("trim=end_frame=9", graph)
        self.assertIn("trim=end_frame=13", graph)
        self.assertIn("tpad=stop_mode=clone:stop=-1", graph)
        self.assertIn("apad=pad_dur=1,atrim=end=0.360000", graph)
        self.assertIn("atrim=end=0.520000", graph)
        self.assertIn("trim=start=1.040000:end=1.400000", graph)
        self.assertIn("concat=n=2:v=1:a=1", graph)

    def test_progress_uses_written_time_and_speed(self):
        self.assertEqual(render_roughcut.parse_clock("00:01:02.500000"), 62.5)
        self.assertEqual(render_roughcut.parse_clock("N/A"), 0.0)
        self.assertEqual(render_roughcut.parse_clock("01:00:00.000000"), 3600.0)
        self.assertIsNone(render_roughcut.parse_speed("N/A"))
        self.assertEqual(render_roughcut.parse_speed("1.25x"), 1.25)
        mid = render_roughcut.progress_snapshot(50, 2, 100, False)
        self.assertEqual(mid["fraction"], 0.5)
        self.assertEqual(mid["remaining"], 25)
        early = render_roughcut.progress_snapshot(0, None, 100, False)
        self.assertEqual(early["fraction"], 0)
        self.assertIsNone(early["remaining"])
        done = render_roughcut.progress_snapshot(100, 1, 100, True)
        self.assertEqual(done["fraction"], 1.0)
        self.assertIsNone(done["remaining"])
        over = render_roughcut.progress_snapshot(120, 1, 100, False)
        self.assertEqual(over["fraction"], 0.99)


if __name__ == "__main__":
    unittest.main()
