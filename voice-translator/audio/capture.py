import pyaudio
import numpy as np
import wave
import tempfile
import asyncio
from typing import Optional
import config
import os


class AudioCapture:
    def __init__(self):
        self.chunk_size = 4096
        self.sample_rate = 16000
        self.channels = 1
        self.format = pyaudio.paInt16
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.audio_buffer = []

    async def start(self):
        self.is_listening = True
        self.audio = pyaudio.PyAudio()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._start_stream)

    def _start_stream(self):
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._audio_callback,
        )
        self.stream.start_stream()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        if status:
            print(f"Audio callback status: {status}")

        if self.is_listening:
            self.audio_buffer.append(in_data)

        return (in_data, pyaudio.paContinue)

    async def stop(self):
        self.is_listening = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio:
            self.audio.terminate()
            self.audio = None

        self.audio_buffer = []

    async def capture_chunk(self, duration: int = 3) -> Optional[str]:
        if not self.is_listening:
            return None

        await asyncio.sleep(duration)

        if not self.audio_buffer:
            return None

        audio_data = b"".join(self.audio_buffer)
        self.audio_buffer = []

        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

        with wave.open(temp_file.name, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)

        return temp_file.name
