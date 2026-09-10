# Multi-Model Chatbot

A local multi-model chatbot with a browser UI, CLI, and FastAPI backend. It uses LangChain's common runnable interface for Gemini, Groq, and Ollama, and includes LangChain Community for the broader integration ecosystem. OpenAI and Anthropic remain available behind the same provider abstraction. Sessions are persisted to `data/sessions.json` after every message.

## Features

- Browser-based chat UI served from the FastAPI app
- Terminal-based chat via the CLI client
- Support for multiple providers: OpenAI, Anthropic, Gemini, Groq, and local Ollama
- Session persistence and history lookup
- Model listing and availability checks

## Install

Use Python 3.10 or newer. Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
Copy-Item .env.example .env
```

Edit `.env` and add the API key for the provider you intend to use. For Ollama, start Ollama locally and make sure `OLLAMA_MODEL` names a downloaded model. The default is Gemini; set `DEFAULT_MODEL` to `groq` or `local` if that better matches your setup.

## Run

Start the backend in one terminal:

```powershell
uvicorn app.main:app --reload
```

Open the browser UI at:

```text
http://localhost:8000/
```

You can also use the CLI in another terminal:

```powershell
chatbot chat --model gemini
chatbot chat --model groq
chatbot chat --model local
```

You can resume a conversation with `chatbot chat --session <id>`. The CLI prints a session ID after each reply. If you do not install the command entry point, use `python -m cli.main chat` instead.

## Commands

```powershell
chatbot --version
chatbot sessions list
chatbot models list
```

Set `CHATBOT_BACKEND_URL` to use a backend other than `http://localhost:8000`.

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Browser UI entry point |
| `GET` | `/health` | Service health and version |
| `POST` | `/chat` | Full non-streaming reply |
| `POST` | `/chat/stream` | Server-sent-event token stream |
| `GET` | `/sessions` | Session summaries |
| `GET` | `/sessions/{id}` | Session history |
| `GET` | `/models` | Provider/model availability |

Example non-streaming request:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/chat -ContentType 'application/json' -Body '{"message":"Hello", "model":"local"}'
```
