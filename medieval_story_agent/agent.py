"""Core medieval story generation logic."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryRequest:
    """Normalized story-writing request."""

    topic: str
    language: str = "vi"
    tone: str = "epic"
    length: str = "medium"
    protagonist: str = ""
    setting: str = ""


class MedievalStoryAgent:
    """A local medieval story writer with optional LLM prompt support."""

    _TONES = {
        "epic": "hao hung, trang trong, co chat su thi",
        "dark": "u toi, bi an, day bat trac",
        "romantic": "lang man, mong manh, giau cam xuc",
        "humorous": "hai huoc nhe, duyen dang, am ap",
    }
    _LENGTHS = {
        "short": 3,
        "medium": 5,
        "long": 8,
    }

    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)

    @property
    def tones(self) -> tuple[str, ...]:
        return tuple(self._TONES.keys())

    @property
    def lengths(self) -> tuple[str, ...]:
        return tuple(self._LENGTHS.keys())

    def normalize_request(self, payload: dict[str, object]) -> StoryRequest:
        topic = str(payload.get("topic") or payload.get("prompt") or payload.get("message") or "").strip()
        if not topic:
            topic = "mot hiep si tre di tim thanh kiem that lac"

        language = str(payload.get("language") or "vi").strip().lower()
        tone = str(payload.get("tone") or "epic").strip().lower()
        length = str(payload.get("length") or "medium").strip().lower()
        protagonist = str(payload.get("protagonist") or "").strip()
        setting = str(payload.get("setting") or "").strip()

        if tone not in self._TONES:
            available = ", ".join(self.tones)
            raise ValueError(f"Unknown tone '{tone}'. Choose one of: {available}.")

        if length not in self._LENGTHS:
            available = ", ".join(self.lengths)
            raise ValueError(f"Unknown length '{length}'. Choose one of: {available}.")

        return StoryRequest(
            topic=topic,
            language=language,
            tone=tone,
            length=length,
            protagonist=protagonist,
            setting=setting,
        )

    def write_story(self, request: StoryRequest) -> dict[str, object]:
        """Generate a complete local story without network calls."""
        title = self._title(request)
        outline = self._outline(request)
        story = self._story(request, title, outline)

        return {
            "title": title,
            "story": story,
            "outline": outline,
            "metadata": {
                "genre": "medieval fantasy",
                "language": request.language,
                "tone": request.tone,
                "length": request.length,
            },
        }

    def llm_prompt(self, request: StoryRequest) -> list[dict[str, str]]:
        """Build messages for an OpenAI-compatible chat model."""
        paragraph_count = self._LENGTHS[request.length]
        return [
            {
                "role": "system",
                "content": (
                    "You are a medieval fantasy author. Write vivid, coherent stories with castles, "
                    "knights, guilds, oaths, court intrigue, old magic, and concrete sensory detail. "
                    "Avoid modern slang and avoid explaining your process. Return a JSON object with "
                    "keys: title, story, outline, metadata. Do not include markdown fences."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Language: {request.language}\n"
                    f"Topic: {request.topic}\n"
                    f"Tone: {request.tone} ({self._TONES[request.tone]})\n"
                    f"Length: about {paragraph_count} paragraphs\n"
                    f"Protagonist: {request.protagonist or 'choose a suitable medieval protagonist'}\n"
                    f"Setting: {request.setting or 'choose a rich medieval setting'}\n"
                    "Write the story now."
                ),
            },
        ]

    def _title(self, request: StoryRequest) -> str:
        seeds = [
            "Loi The Duoi Thap Chuong",
            "Thanh Kiem Trong Suong Som",
            "Lau Dai Ben Rung Den",
            "Vuong Mien Cua Ke Khong Ngai",
            "Nguoi Gac Cong Thanh Co",
        ]
        if request.topic:
            key = request.topic[:42].strip(" .,!?:;")
            return f"Truyen Trung Co: {key.title()}"
        return self._random.choice(seeds)

    def _outline(self, request: StoryRequest) -> list[str]:
        hero = request.protagonist or self._random.choice(["mot hiep si tre", "co nu tho ren", "nguoi linh gac cong"])
        place = request.setting or self._random.choice(["thanh da xam Eldermark", "tu vien tren dinh nui", "ben cang mua dong"])
        return [
            f"{hero} nhan duoc loi trieu tap tai {place}.",
            "Mot bi mat cu cua vuong quoc bi danh thuc.",
            "Nhan vat chinh phai chon giua loi the, tinh than va su that.",
            "Cai gia cua chien thang de lai mot dau an lau dai.",
        ]

    def _story(self, request: StoryRequest, title: str, outline: list[str]) -> str:
        hero = request.protagonist or "chang hiep si tre Alaric"
        place = request.setting or "lau dai da xam nam ben ria rung thong"
        tone_detail = self._TONES[request.tone]
        paragraphs = [
            (
                "Trong nhung nam thang ma tieng chuong nha tho con vang qua cac thung lung, "
                f"{hero} den {place} voi mot loi thinh cau duoc niem bang sap ong do. "
                f"Dan lang noi rang cau chuyen ve {request.topic} khong con la loi don, "
                "ma da tro thanh bong toi bo qua cong thanh moi dem."
            ),
            (
                "Tai dai sanh, lanh chua gia trao cho nguoi khach mot tam ban do rach mep va "
                "mot chiec nhan sat lanh. Tren mat nhan khac dau an cua mot dong ho da bien mat "
                "sau tran chien mua dong. Khong ai trong trieu dinh dam nhac ten ho, vi moi loi "
                "thia thot ve qua khu deu khien lua trong lo suoi chao dao."
            ),
            (
                f"Chuyen di mang sac thai {tone_detail}. Qua cau da phu reu, qua cho phien day "
                "mui long cuu va khoi than, nhan vat chinh gap nhung ke buon tin, mot thay tu "
                "giu cuon bien nien su cam, va mot dua tre biet bai hat cua nguoi chet. Moi "
                "manh moi deu dan ve toa thap bi niem phong sau rung sam."
            ),
            (
                "Khi cong thap mo ra, su that khong nam trong vang bac hay phep thuat, ma trong "
                "mot loi the bi phan boi. Nguoi anh hung hieu rang vuong quoc duoc cuu khong phai "
                "bang luoi kiem sac nhat, ma bang viec noi ra dieu ma nhung ke quyen quy da chon "
                "chinh vang trong im lang."
            ),
            (
                "Binh minh hom sau, co hieu tren thanh khong con bay cung huong gio cu. Dan chung "
                "ke lai cau chuyen ay ben lua bep, moi lan lai them mot chi tiet khac, nhung ai "
                "tung nghe tieng chuong dem do deu biet: mot thoi dai da khep lai, va mot loi the "
                "moi vua duoc ren trong tro tan."
            ),
        ]
        return "\n\n".join(paragraphs[: self._LENGTHS[request.length]])
