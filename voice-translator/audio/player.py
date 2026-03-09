import discord
import asyncio
from typing import Optional


class AudioPlayer:
    def __init__(self, voice_client: discord.VoiceClient):
        self.voice_client = voice_client
        self.is_playing = False
        self.current_task = None

    async def play(self, audio_path: str) -> bool:
        if not self.voice_client or not self.voice_client.is_connected():
            return False

        while self.voice_client.is_playing():
            await asyncio.sleep(0.1)

        source = discord.FFmpegPCMAudio(
            audio_path, executable="ffmpeg", options="-af 'volume=0.5'"
        )

        transformed = discord.PCMVolumeTransformer(source)
        transformed.volume = 0.5

        def after_playing(error):
            if error:
                print(f"Playback error: {error}")
            self.is_playing = False

        self.voice_client.play(transformed, after=after_playing)
        self.is_playing = True

        while self.voice_client.is_playing():
            await asyncio.sleep(0.1)

        return True

    async def stop(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.is_playing = False
