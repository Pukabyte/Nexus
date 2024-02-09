import re
import PTN
from typing import List


class Parser:
    """Parse a string and return the parsed data."""

    def __init__(self):
        self.resolution = ["UHD", "2160p", "4K", "1080p", "720p", "480p"]
        self.parsed_data = None

    def parse(self, string) -> dict:
        """Parse the given string and return the parsed data."""
        if not self.parsed_data:
            self._parse(string)
        return self.parsed_data

    def _parse(self, string) -> dict:
        """Parse the given string and return the parsed data."""
        parse = PTN.parse(string)
        title = parse.get("title", "")
        episodes = self._get_episodes(parse)
        is_4k = parse.get("resolution", False) in ["2160p", "4K", "UHD"]
        self.parsed_data = {
            "string": string,
            "title": title,
            "fetch": False,
            "is_4k": is_4k,
            "is_dual_audio": self.is_dual_audio(string),
            "is_complete": self.is_complete_series(string),
            "is_unwanted_quality": self.is_unwanted_quality(string),
            "year": parse.get("year", False),
            "resolution": parse.get("resolution", []),
            "quality": parse.get("quality", []),
            "season": parse.get("season", []),
            "episodes": episodes,
            "codec": parse.get("codec", []),
            "audio": parse.get("audio", []),
            "hdr": parse.get("hdr", False),
            "upscaled": parse.get("upscaled", False),
            "remastered": parse.get("remastered", False),
            "proper": parse.get("proper", False),
            "repack": parse.get("repack", False),
            "subtitles": parse.get("subtitles") == "Available",
            "language": parse.get("language", []),
            "remux": parse.get("remux", False),
            "extended": parse.get("extended", []),
        }

        # Determine if this item should be fetched
        self.parsed_data["fetch"] = self._should_fetch(self.parsed_data)

    def seasons(self, string) -> List[int]:
        """Return a list of seasons mentioned in the given string."""
        if not self.parsed_data:
            self._parse(string)
        return self.parsed_data["season"]

    @staticmethod
    def _parse_season_range(season_str):
        """Parse a season range and return a list of season numbers."""
        seasons = []
        ranges = season_str.split("-")
        if len(ranges) == 2:
            start = int(ranges[0])
            end = int(ranges[1])
            seasons.extend(range(start, end + 1))
        return seasons

    def _get_episodes(self, parse):
        episodes = []
        if parse.get("episode", False):
            episode = parse.get("episode")
            if isinstance(episode, list):
                episodes.extend(int(sub_episode) for sub_episode in episode)
            else:
                episodes.append(int(episode))
        return episodes

    def episodes(self, string) -> List[int]:
        """Return a list of episodes in the given string."""
        if not self.parsed_data:
            self._parse(string)
        return self.parsed_data["episodes"]

    def episodes_in_season(self, season, string) -> List[int]:
        """Return a list of episodes in the given season."""
        parse = self._parse(string=string)
        if parse["season"] == season:
            return parse["episodes"]
        return []

    def _should_fetch(self, parsed_data: dict) -> bool:
        """Determine if the parsed content should be fetched."""
        # This is where we determine if the item should be fetched
        # Edit with caution. All have to match for the item to be fetched.
        return (
            parsed_data["resolution"] in self.resolution
            and not parsed_data["is_unwanted_quality"]
        )

    @staticmethod
    def is_highest_quality(parsed_data: dict) -> bool:
        """Check if content is `highest quality`."""
        return any(
            parsed.get("resolution") in ["UHD", "2160p", "4K"]
            or parsed.get("hdr", False)
            or parsed.get("remux", False)
            or parsed.get("upscaled", False)
            for parsed in parsed_data
        )

    @staticmethod
    def is_dual_audio(string) -> bool:
        """Check if any content in parsed_data has dual audio."""
        dual_audio_patterns = [
            re.compile(
                r"\bmulti(?:ple)?[ .-]*(?:lang(?:uages?)?|audio|VF2)?\b", re.IGNORECASE
            ),
            re.compile(r"\btri(?:ple)?[ .-]*(?:audio|dub\w*)\b", re.IGNORECASE),
            re.compile(r"\bdual[ .-]*(?:au?$|[aá]udio|line)\b", re.IGNORECASE),
            re.compile(r"\bdual\b(?![ .-]*sub)", re.IGNORECASE),
            re.compile(r"\b(?:audio|dub(?:bed)?)[ .-]*dual\b", re.IGNORECASE),
            re.compile(r"\bengl?(?:sub[A-Z]*)?\b", re.IGNORECASE),
            re.compile(r"\beng?sub[A-Z]*\b", re.IGNORECASE),
            re.compile(r"\b(?:DUBBED|dublado|dubbing|DUBS?)\b", re.IGNORECASE),
        ]
        return any(pattern.search(string) for pattern in dual_audio_patterns)

    @staticmethod
    def is_complete_series(string) -> bool:
        """Check if string is a `complete series`."""
        series_patterns = [
            re.compile(
                r"(?:\bthe\W)?(?:\bcomplete|collection|dvd)?\b[ .]?\bbox[ .-]?set\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"(?:\bthe\W)?(?:\bcomplete|collection|dvd)?\b[ .]?\bmini[ .-]?series\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"(?:\bthe\W)?(?:\bcomplete|full|all)\b.*\b(?:series|seasons|collection|episodes|set|pack|movies)\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"\b(?:series|seasons|movies?)\b.*\b(?:complete|collection)\b",
                re.IGNORECASE,
            ),
            re.compile(r"(?:\bthe\W)?\bultimate\b[ .]\bcollection\b", re.IGNORECASE),
            re.compile(r"\bcollection\b.*\b(?:set|pack|movies)\b", re.IGNORECASE),
            re.compile(r"\bcollection\b", re.IGNORECASE),
            re.compile(
                r"duology|trilogy|quadr[oi]logy|tetralogy|pentalogy|hexalogy|heptalogy|anthology|saga",
                re.IGNORECASE,
            ),
        ]
        return any(pattern.search(string) for pattern in series_patterns)

    @staticmethod
    def is_unwanted_quality(string) -> bool:
        """Check if string has an 'unwanted' quality. Default to False."""
        unwanted_patterns = [
            re.compile(
                r"\b(?:H[DQ][ .-]*)?CAM(?:H[DQ])?(?:[ .-]*Rip)?\b", re.IGNORECASE
            ),
            re.compile(r"\b(?:H[DQ][ .-]*)?S[ .-]*print\b", re.IGNORECASE),
            re.compile(r"\b(?:HD[ .-]*)?T(?:ELE)?S(?:YNC)?(?:Rip)?\b", re.IGNORECASE),
            re.compile(r"\b(?:HD[ .-]*)?T(?:ELE)?C(?:INE)?(?:Rip)?\b", re.IGNORECASE),
            re.compile(r"\bP(?:re)?DVD(?:Rip)?\b", re.IGNORECASE),
            re.compile(r"\b(?:DVD?|BD|BR)?[ .-]*Scr(?:eener)?\b", re.IGNORECASE),
            re.compile(r"\bVHS\b", re.IGNORECASE),
            re.compile(r"\bHD[ .-]*TV(?:Rip)?\b", re.IGNORECASE),
            re.compile(r"\bDVB[ .-]*(?:Rip)?\b", re.IGNORECASE),
            re.compile(r"\bSAT[ .-]*Rips?\b", re.IGNORECASE),
            re.compile(r"\bTVRips?\b", re.IGNORECASE),
            re.compile(r"\bR5|R6\b", re.IGNORECASE),
            re.compile(r"\b(DivX|XviD)\b", re.IGNORECASE),
        ]
        return any(pattern.search(string) for pattern in unwanted_patterns)


parser = Parser()
