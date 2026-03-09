import asyncio
import discord
from discord import app_commands
import config
from translate.stt import STTHandler
from translate.translator import Translator
from translate.tts import TTSHandler
from audio.capture import AudioCapture
from audio.player import AudioPlayer
import tempfile
import os


class VoiceTranslatorBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)
        self.voice_client = None

        self.target_lang = "es"
        self.source_lang = "en"

        self.stt = STTHandler()
        self.translator = Translator()
        self.tts = TTSHandler()

        self.capture = None
        self.player = None
        self.is_translating = False
        self.translation_task = None

    async def setup_hook(self):
        await self.tree.sync()
        await self.stt.initialize()

    async def translate_loop(self):
        self.is_translating = True

        while self.is_translating:
            try:
                audio_file = await self.capture.capture_chunk(
                    duration=config.CHUNK_DURATION
                )

                if audio_file and os.path.exists(audio_file):
                    text = await self.stt.transcribe(
                        audio_file, language=self.source_lang
                    )

                    if text and len(text) > 2:
                        translated = await self.translator.translate(
                            text,
                            source_lang=self.source_lang,
                            target_lang=self.target_lang,
                        )

                        if translated:
                            tts_file = tempfile.NamedTemporaryFile(
                                suffix=".mp3", delete=False
                            )
                            await self.tts.synthesize(
                                translated, self.target_lang, tts_file.name
                            )
                            await self.player.play(tts_file.name)
                            os.unlink(tts_file.name)

                    if os.path.exists(audio_file):
                        os.unlink(audio_file)

                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Error in translation loop: {e}")
                await asyncio.sleep(1)

    async def join_voice(self, channel: discord.VoiceChannel):
        if self.voice_client:
            await self.leave_voice()

        self.voice_client = await channel.connect(self_mute=False, self_deaf=False)

        self.capture = AudioCapture()
        self.player = AudioPlayer(self.voice_client)

        await self.capture.start()

        self.translation_task = asyncio.create_task(self.translate_loop())

        return self.voice_client

    async def leave_voice(self):
        self.is_translating = False

        if self.translation_task:
            self.translation_task.cancel()
            try:
                await self.translation_task
            except asyncio.CancelledError:
                pass

        if self.capture:
            await self.capture.stop()

        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None

        self.capture = None
        self.player = None


bot = VoiceTranslatorBot()


@bot.tree.command()
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message(
            "You're not in a voice channel!", ephemeral=True
        )
        return

    await interaction.response.defer()

    channel = interaction.user.voice.channel
    await bot.join_voice(channel)

    await interaction.followup.send(
        f"Joined {channel.name}. Translating from {config.AVAILABLE_LANGUAGES[bot.source_lang]} to {config.AVAILABLE_LANGUAGES[bot.target_lang]}!\n\n"
        f"Make sure your microphone is enabled and speaking."
    )


@bot.tree.command()
async def leave(interaction: discord.Interaction):
    await bot.leave_voice()
    await interaction.response.send_message("Left the voice channel.")


@bot.tree.command()
async def lang(interaction: discord.Interaction, language: str):
    if language not in config.AVAILABLE_LANGUAGES:
        await interaction.response.send_message(
            f"Invalid language code. Use `/langs` to see available codes.",
            ephemeral=True,
        )
        return

    bot.target_lang = language
    await interaction.response.send_message(
        f"Target language set to {config.AVAILABLE_LANGUAGES[language]} ({language})"
    )


@bot.tree.command()
async def langs(interaction: discord.Interaction):
    lang_list = ", ".join(
        [f"`{code}` - {name}" for code, name in config.AVAILABLE_LANGUAGES.items()]
    )
    await interaction.response.send_message(
        f"Available languages:\n{lang_list}", ephemeral=True
    )


@bot.tree.command()
async def source(interaction: discord.Interaction, language: str):
    if language not in config.AVAILABLE_LANGUAGES:
        await interaction.response.send_message(
            f"Invalid language code. Use `/langs` to see available codes.",
            ephemeral=True,
        )
        return

    bot.source_lang = language
    await interaction.response.send_message(
        f"Source language set to {config.AVAILABLE_LANGUAGES[language]} ({language})"
    )


async def main():
    if not config.DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not set in .env")
        return

    await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
