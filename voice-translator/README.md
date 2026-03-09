# Voice Translator Bot

Discord bot that translates voice in real-time from English to your target language.

## Setup

### 1. Install Dependencies

```bash
cd ~/fgtdash/voice-translator
pip install -r requirements.txt
```

**Note**: PyAudio may need system dependencies:

- **Linux**: `sudo apt install portaudio19-dev python3-pyaudio`
- **Mac**: `brew install portaudio`
- **Windows**: Usually installs automatically via pip

### 2. Configure Environment

Edit `.env` and add your credentials:

```env
DISCORD_TOKEN=your_discord_token_here
AZURE_KEY=your_azure_translator_key_here
AZURE_ENDPOINT=https://api.cognitive.microsofttranslator.com
```

**Getting Discord Token:**

- Enable Developer Mode in Discord
- Press Ctrl+Shift+I → Application → Local Storage → token

**Getting Azure Key:**

- Go to https://portal.azure.com/
- Create Translator resource
- Keys and Endpoint section

### 3. Run the Bot

```bash
python main.py
```

## How It Works

This bot uses **microphone capture** (Option 2) for reliable voice translation:

1. Bot joins your voice channel
2. Your microphone captures your speech directly (via PyAudio)
3. faster-whisper transcribes speech to text
4. Azure Translator converts text to target language
5. Edge TTS synthesizes translated audio
6. Bot plays translated audio in VC

**Benefits**: No Discord API audio limitations, clean audio path, works reliably.

## Commands

| Command          | Description                            |
| ---------------- | -------------------------------------- |
| `!join`          | Bot joins your voice channel           |
| `!leave`         | Bot leaves voice channel               |
| `!lang <code>`   | Set target language (e.g., `!lang es`) |
| `!source <code>` | Set source language (default: English) |
| `!langs`         | List all available languages           |

## Usage

1. Join a voice channel
2. Run `!join` - bot will join and start listening to your mic
3. Set target language with `!lang <code>`
4. Speak into your microphone - bot will translate and play in VC
5. Run `!leave` when done

## Language Codes

Common codes: `en`, `es`, `fr`, `de`, `it`, `pt`, `ru`, `ja`, `ko`, `zh`, `ar`, `hi`

Full list: `!langs`

## Requirements

- Python 3.10+
- FFmpeg installed
- Microphone connected and accessible
- Working microphone permissions

## Notes

- First run downloads Whisper model (~140MB for base model)
- Audio processed in 3-second chunks
- Requires FFmpeg installed (`sudo apt install ffmpeg`)
- Make sure your microphone is set as default input device
