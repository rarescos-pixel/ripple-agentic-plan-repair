#!/usr/bin/env python3
"""Validate a Ripple submission master with ffprobe.

Usage:
    python video/validate_master.py path/to/ripple-demo-master.mp4

This checks mechanical delivery constraints only. It does not certify claim accuracy,
visual quality, or that the footage matches the VIDEO FREEZE packet.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
MAX_DURATION_SECONDS = 180.0
TARGET_MAX_SECONDS = 145.0  # editorial target 2:25, warning only


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate_master.py <video-file>")

    video = Path(sys.argv[1])
    if not video.is_file():
        fail(f"file not found: {video}")

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        fail("ffprobe is not installed or not on PATH")

    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(video),
    ]
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        fail(f"ffprobe failed: {exc.stderr.strip()}")

    data = json.loads(proc.stdout)
    streams = data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    if len(video_streams) != 1:
        fail(f"expected exactly one video stream, found {len(video_streams)}")
    if not audio_streams:
        fail("no audio stream found")

    v = video_streams[0]
    width = int(v.get("width") or 0)
    height = int(v.get("height") or 0)
    if (width, height) != (TARGET_WIDTH, TARGET_HEIGHT):
        fail(f"expected {TARGET_WIDTH}x{TARGET_HEIGHT}, got {width}x{height}")

    vcodec = (v.get("codec_name") or "").lower()
    if vcodec != "h264":
        fail(f"expected H.264 video, got {vcodec or 'unknown'}")

    duration_raw = data.get("format", {}).get("duration")
    try:
        duration = float(duration_raw)
    except (TypeError, ValueError):
        fail("unable to determine duration")

    if duration >= MAX_DURATION_SECONDS:
        fail(f"duration must be < {MAX_DURATION_SECONDS:.0f}s, got {duration:.3f}s")

    audio_codecs = {(s.get("codec_name") or "").lower() for s in audio_streams}
    if "aac" not in audio_codecs:
        fail(f"expected at least one AAC audio stream, got {sorted(audio_codecs)}")

    frame_rate = v.get("avg_frame_rate") or v.get("r_frame_rate") or "unknown"

    print("PASS: mechanical master validation")
    print(f"file={video}")
    print(f"duration_seconds={duration:.3f}")
    print(f"resolution={width}x{height}")
    print(f"video_codec={vcodec}")
    print(f"audio_codecs={','.join(sorted(audio_codecs))}")
    print(f"frame_rate={frame_rate}")

    if duration > TARGET_MAX_SECONDS:
        print(
            f"WARN: duration exceeds editorial target of {TARGET_MAX_SECONDS:.0f}s; "
            "review for pacing/filler even though it is rule-compliant"
        )


if __name__ == "__main__":
    main()
