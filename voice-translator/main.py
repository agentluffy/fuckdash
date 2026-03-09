import asyncio
import discord
from discord.ext import commands
import config
from translate.stt import STTHandler
from translate.translator import Translator
from translate.tts import TTSHandler
from audio.capture import AudioCapture
from audio.player import AudioPlayer
import tempfile
import os


bot = commands.Bot(command_prefix="!", self_bot=True, intents=discord.Intents.default())

voice_client = None
target_lang = "es"
source_lang = "en"

stt = STTHandler()
translator = Translator()
tts = TTSHandler()

capture = None
player = None
is_translating = False
translation_task = None


async def translate_loop():
    global is_translating
    is_translating = True

    while is_translating:
        try:
            audio_file = await capture.capture_chunk(duration=config.CHUNK_DURATION)

            if audio_file and os.path.exists(audio_file):
                text = await stt.transcribe(audio_file, language=source_lang)

                if text and len(text) > 2:
                    translated = await translator.translate(
                        text,
                        source_lang=source_lang,
                        target_lang=target_lang,
                    )

                    if translated:
                        tts_file = tempfile.NamedTemporaryFile(
                            suffix=".mp3", delete=False
                        )
                        await tts.synthesize(translated, target_lang, tts_file.name)
                        await player.play(tts_file.name)
                        os.unlink(tts_file.name)

                if os.path.exists(audio_file):
                    os.unlink(audio_file)

            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error in translation loop: {e}")
            await asyncio.sleep(1)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await stt.initialize()


@bot.command()
async def join(ctx):
    global voice_client, capture, player, translation_task

    if not ctx.author.voice:
        await ctx.send("You're not in a voice channel!")
        return

    channel = ctx.author.voice.channel

    if voice_client:
        await voice_client.disconnect()

    voice_client = await channel.connect(self_mute=False, self_deaf=False)

    capture = AudioCapture()
    player = AudioPlayer(voice_client)

    await capture.start()

    translation_task = asyncio.create_task(translate_loop())

    await ctx.send(
        f"Joined {channel.name}. Translating from {config.AVAILABLE_LANGUAGES[source_lang]} to {config.AVAILABLE_LANGUAGES[target_lang]}!\n\n"
        f"Make sure your microphone is enabled and speaking."
    )


@bot.command()
async def leave(ctx):
    global voice_client, capture, player, is_translating

    is_translating = False

    if translation_task:
        translation_task.cancel()
        try:
            await translation_task
        except asyncio.CancelledError:
            pass

    if capture:
        await capture.stop()

    if voice_client:
        await voice_client.disconnect()
        voice_client = None

    capture = None
    player = None

    await ctx.send("Left the voice channel.")


@bot.command()
async def lang(ctx, language: str):
    global target_lang

    if language not in config.AVAILABLE_LANGUAGES:
        await ctx.send(f"Invalid language code. Use `!langs` to see available codes.")
        return

    target_lang = language
    await ctx.send(
        f"Target language set to {config.AVAILABLE_LANGUAGES[language]} ({language})"
    )


@bot.command()
async def langs(ctx):
    lang_list = ", ".join(
        [f"`{code}` - {name}" for code, name in config.AVAILABLE_LANGUAGES.items()]
    )
    await ctx.send(f"Available languages:\n{lang_list}")


@bot.command()
async def source(ctx, language: str):
    global source_lang

    if language not in config.AVAILABLE_LANGUAGES:
        await ctx.send(f"Invalid language code. Use `!langs` to see available codes.")
        return

    source_lang = language
    await ctx.send(
        f"Source language set to {config.AVAILABLE_LANGUAGES[language]} ({language})"
    )


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not set in .env")
    else:
        bot.run(config.DISCORD_TOKEN)
