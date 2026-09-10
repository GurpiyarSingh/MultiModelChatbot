import asyncio
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from cli.client import ChatbotClient

app = typer.Typer(help="CLI client for the Multi-Model Chatbot.", no_args_is_help=True)
sessions_app = typer.Typer(help="Inspect saved chat sessions.")
models_app = typer.Typer(help="Inspect usable models.")
app.add_typer(sessions_app, name="sessions")
app.add_typer(models_app, name="models")
console = Console()
BACKEND_URL = os.getenv("CHATBOT_BACKEND_URL", "http://localhost:8000")
VERSION = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()


def version_callback(value: bool) -> None:
    if value:
        console.print(VERSION)
        raise typer.Exit()


@app.callback()
def root(version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True)) -> None:
    """Chat with models through a local FastAPI backend."""


@app.command()
def chat(
    model: str | None = typer.Option(None, "--model", "-m"),
    session: str | None = typer.Option(None, "--session", "-s"),
) -> None:
    """Start an interactive streaming chat. Type /exit to leave."""
    async def run() -> None:
        nonlocal session
        client = ChatbotClient(BACKEND_URL)
        console.print("[dim]Type /exit to end the chat.[/dim]")
        while True:
            try:
                prompt = console.input("[bold cyan]You> [/bold cyan]").strip()
            except (EOFError, KeyboardInterrupt):
                console.print()
                return
            if prompt.lower() in {"/exit", "/quit", "exit", "quit"}:
                return
            if not prompt:
                continue
            console.print("[bold green]Assistant>[/bold green] ", end="")
            try:
                async for event in client.chat_stream(prompt, model, session):
                    if event["type"] == "token":
                        console.print(event["content"], end="")
                    elif event["type"] == "done":
                        session = event["session_id"]
                    elif event["type"] == "error":
                        console.print(f"\n[red]Error: {event['detail']}[/red]")
                console.print()
                if session:
                    console.print(f"[dim]Session: {session}[/dim]")
            except httpx.HTTPError as exc:  # type: ignore[name-defined]
                console.print(f"\n[red]Backend error: {exc}[/red]")
    import httpx
    asyncio.run(run())


@sessions_app.command("list")
def sessions_list() -> None:
    async def run() -> None:
        rows = await ChatbotClient(BACKEND_URL).get("/sessions")
        table = Table("Session", "Model", "Messages", "Updated")
        for row in rows:
            table.add_row(row["id"], row["model"], str(row["message_count"]), row["updated_at"])
        console.print(table)
    asyncio.run(run())


@models_app.command("list")
def models_list() -> None:
    async def run() -> None:
        rows = await ChatbotClient(BACKEND_URL).get("/models")
        table = Table("Model", "Provider", "Available")
        for row in rows:
            table.add_row(row["id"], row["provider"], "yes" if row["available"] else "no")
        console.print(table)
    asyncio.run(run())


if __name__ == "__main__":
    app()
