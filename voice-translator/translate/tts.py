import asyncio
import edge_tts
from typing import Optional
import config


VOICE_MAP = {
    "en": "en-US-AriaNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ar": "ar-SA-ZoeNeural",
    "hi": "hi-IN-SwaraNeural",
    "nl": "nl-NL-ColetteNeural",
    "pl": "pl-PL-AgnieszkaNeural",
    "tr": "tr-TR-SedaNeural",
    "vi": "vi-VN-LinhNeural",
    "th": "th-TH-PremwanNeural",
    "sv": "sv-SE-SofieNeural",
    "da": "da-DK-SigneNeural",
    "fi": "fi-FI-SelmaNeural",
    "no": "no-NO-IselinNeural",
    "cs": "cs-CZ-VlastaNeural",
    "el": "el-GR-AthinaNeural",
    "he": "he-IL-HilaNeural",
    "hu": "hu-HU-NoemiNeural",
    "id": "id-ID-GadisNeural",
    "ms": "ms-MY-YasminNeural",
    "ro": "ro-RO-AlinaNeural",
    "sk": "sk-SK-LukasNeural",
    "uk": "uk-UA-PolinaNeural",
}


class TTSHandler:
    def __init__(self):
        self.voice_map = VOICE_MAP

    async def synthesize(
        self, text: str, lang: str = "en", output_path: str = "output.mp3"
    ) -> Optional[str]:
        if not text:
            return None

        voice = self.voice_map.get(lang, self.voice_map["en"])

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

        return output_path
