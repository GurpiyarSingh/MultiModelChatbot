# Multi-Model Chatbot Prototype

A small, single-user chatbot backend and terminal client. It uses LangChain's common runnable interface for Gemini, Groq, and Ollama, and includes LangChain Community for the broader LangChain integration ecosystem. OpenAI and Anthropic remain available behind the same provider interface. Sessions are held in memory and saved to `data/sessions.json` after every message.

## Install

Use Python 3.10 or newer. Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
Copy-Item .env.example .env
```

Edit `.env` and add the API key for the provider you plan to use. For Ollama, start Ollama locally and make sure `OLLAMA_MODEL` names a downloaded model. The default is Gemini; set `DEFAULT_MODEL` to `groq` or `local` if that better matches your setup.

## Run

Start the backend in one terminal:

```powershell
uvicorn app.main:app --reload
```

In another terminal, start a streaming chat:

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
