# Local Languages AI API

A multilingual AI API supporting Yoruba, Hausa, Igbo, and 6 other languages. It is built with FastAPI, Spitch and Groq LLM.

## What it does

This project lets you translate text, transcribe speech, and generate audio across African and world languages. It runs as a REST API and comes with a Gradio web interface you can share with anyone.

## Features

- **Translation**: Translates between 9 languages using Groq (LLaMA 3.3 70B), with attention to tone and cultural meaning
- **Speech-to-Text**: Transcribes audio files using the Spitch API
- **Text-to-Speech**: Converts text to spoken audio via Spitch, with gTTS as a fallback
- **Gradio UI**: Simple 3-tab web interface with a public shareable link

## Supported Languages

Yoruba, Hausa, Igbo, Nigerian Pidgin, English, French, Swahili, Amharic, Arabic

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/translate` | Translate text |
| POST | `/transcribe` | Audio to text |
| POST | `/synthesize` | Text to audio |

## How to Run

Runs in **Google Colab**.

1. Open the notebook in Colab
2. Add your API keys to **Colab Secrets** (lock icon in the sidebar):
   - `Groq_Api_Keys` at (https://console.groq.com)
   - `Spitch_Api_Keys` at (https://spitch.app)
3. Run all cells and the last cell launches a live Gradio link

## Tech Stack

1. FastAPI
2. Pydantic
3. Groq SDK
4. Spitch SDK
5. Gradio
6. gTTS

