import asyncio
from typing import Optional
from faster_whisper import WhisperModel
import config


class STTHandler:
    def __init__(self, model_size: str = "base"):
        self.model = None
        self.model_size = model_size

    async def initialize(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_model)

    def _load_model(self):
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    async def transcribe(self, audio_path: str, language: str = "en") -> Optional[str]:
        if not self.model:
            await self.initialize()

        loop = asyncio.get_event_loop()
        segments, info = await loop.run_in_executor(
            None,
            lambda: self.model.transcribe(audio_path, language=language, beam_size=5),
        )

        text = ""
        async for segment in segments:
            text += segment.text

        return text.strip() if text else None
