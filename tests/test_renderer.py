import json
import pathlib
import sys

import pytest

# Ensure the repository root is on the import path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from Renderer import frames_to_timecode, process_file


def test_frames_to_timecode_basic():
    # 50 frames at 25 fps -> 2 seconds
    assert frames_to_timecode(50, 25) == "00:00:02:00"


def test_process_file(tmp_path):
    sample = {
        "meta": {"fps": "2400", "lang": "en"},
        "events": {
            "0": {
                "start": 0,
                "end": 48,
                "txt": "Hello",
                "annotations": {"0": {"description": "test"}},
                "type": "fn",
                "rgn": "top",
            }
        },
    }

    file_path = tmp_path / "sample.clqtt"
    file_path.write_text(json.dumps(sample))

    with file_path.open("r") as fh:
        csv_content, html_content = process_file(fh)

    assert "Hello" in html_content
    assert "Annotation:" in html_content
    assert "test" in csv_content
