import pytest

from utils.parser import Parser


@pytest.fixture
def parser():
    return Parser()


# Test parser
def test_fetch(parser):
    # Test fetching
    parsed_data = parser.parse(
        "The Mandalorian S02E01 2160p WEB-DL DDP5.1 Atmos HDR HEVC-EVO"
    )
    assert parsed_data["fetch"] == True


def test_parse_resolution(parser):
    # Test parsing resolution
    parsed_data = parser.parse(
        "Casino.1995.MULTi.REMUX.2160p.UHD.Blu-ray.HDR.HEVC.DTS-X7.1-DENDA.mkv"
    )
    assert parsed_data == {
        "string": "Casino.1995.MULTi.REMUX.2160p.UHD.Blu-ray.HDR.HEVC.DTS-X7.1-DENDA.mkv",
        "title": "Casino",
        "fetch": True,
        "is_4k": True,
        "is_dual_audio": True,
        "is_complete": False,
        "is_unwanted_quality": False,
        "year": 1995,
        "resolution": "2160p",
        "quality": "Blu-ray",
        "season": [],
        "episodes": [],
        "codec": "H.265",
        "audio": "DTS:X 7.1",
        "hdr": True,
        "upscaled": False,
        "remastered": False,
        "proper": False,
        "repack": False,
        "subtitles": False,
        "language": [],
        "remux": True,
        "extended": [],
    }


def test_parse_dual_audio(parser):
    # Test parsing dual audio
    parsed_data = parser.parse(
        "[JySzE] Naruto [v2] [R2J] [VFR] [Dual Audio] [Complete] [Extras] [x264]"
    )
    assert parsed_data == {
        "string": "[JySzE] Naruto [v2] [R2J] [VFR] [Dual Audio] [Complete] [Extras] [x264]",
        "title": "Naruto",
        "fetch": False,
        "is_4k": False,
        "is_dual_audio": True,
        "is_complete": False,
        "is_unwanted_quality": False,
        "year": False,
        "resolution": [],
        "quality": [],
        "season": [],
        "episodes": [],
        "codec": "H.264",
        "audio": "Dual",
        "hdr": False,
        "upscaled": False,
        "remastered": False,
        "proper": False,
        "repack": False,
        "subtitles": False,
        "language": [],
        "remux": False,
        "extended": [],
    }


def test_parse_complete_series(parser):
    # Test parsing complete series
    parsed_data = parser.parse(
        "The Sopranos - The Complete Series (Season 1, 2, 3, 4, 5 & 6) + Extras"
    )
    assert parsed_data["is_complete"] == True


def test_parse_unwanted_quality(parser):
    # Test parsing unwanted quality
    parsed_data = parser.parse("Guardians Of The Galaxy 2014 R6 720p HDCAM x264-JYK")
    assert parsed_data["is_unwanted_quality"] == True


if __name__ == "__main__":
    pytest.main()
