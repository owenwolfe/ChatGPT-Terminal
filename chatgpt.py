#!/usr/bin/env python3
"""

This is honestly super nice to have in terminal. I made this very quick and easy but it's super useful to have it in terminal.
I hope you like it.

chatgpt.py — a simple ChatGPT/OpenAI terminal wrapper

What it does:
- Reads your OpenAI API key from the environment variable OPENAI_API_KEY
- Supports 3 modes:
  1) One-shot prompt via command-line args:
       chatgpt explain bfs
  2) Piped stdin:
       cat notes.txt | chatgpt
  3) Interactive REPL (no quotes needed):
       chatgpt
       > explain bfs
       > exit
- Stores conversation history in ~/.chatgpt_history.json
- Allows clearing history:
       chatgpt --reset
"""

import os
import sys
import json
from pathlib import Path
from openai import OpenAI

# Default model if OPENAI_MODEL isn't set in your environment.
# You can change this to another model name you have access to.
MODEL_DEFAULT = "gpt-4.1-mini"

# Where we store your chat history on disk (in your home directory).
HISTORY_PATH = Path.home() / ".chatgpt_history.json"


def load_history():
    """
    Load the conversation history from HISTORY_PATH.

    History format is a list like:
    [
      {"role": "user", "content": "hi"},
      {"role": "assistant", "content": "hello!"}
    ]

    If the file doesn't exist or can't be parsed, return an empty list.
    """
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            # If the JSON file is corrupted, just start fresh.
            return []
    return []


def save_history(history):
    """
    Save conversation history to HISTORY_PATH as JSON.

    We ignore errors on purpose so the CLI still works even if
    disk permissions or file issues happen.
    """
    try:
        HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception:
        pass


def get_prompt_from_args_or_stdin():
    """
    Decide where the prompt comes from.

    Priority:
    1) If there are command line args, treat them as the prompt:
         chatgpt explain bfs
       -> prompt becomes "explain bfs"

    2) Else, if stdin is *not* a TTY, then something is being piped in:
         cat file.txt | chatgpt
       -> prompt becomes the contents of stdin

    3) Else, return empty string (meaning: no prompt provided),
       which will trigger REPL mode in main().
    """

    # sys.argv[0] is the script name; args start at sys.argv[1]
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    # If stdin is not a terminal, we have piped input.
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()

    return ""


def repl(client, history, model):
    """
    REPL

    This avoids quotes entirely to make the user experience more fire: you type a line, press Enter,
    and it sends it to the API. Type 'exit'/'quit' or Ctrl+D to leave.

    It uses the same persistent history file as one-shot mode,
    so it remembers context across runs (unless you --reset).
    """

    print("Welcome to the terminal of GPT (to quit -> 'exit')")
    while True:
        try:
            prompt = input("> ").strip()
        except EOFError:
            # Ctrl+D sends EOF; end the session cleanly.
            print()
            break

        if not prompt:
            # Ignore empty lines
            continue

        if prompt.lower() in {"exit", "quit"}:
            break

        # Add the user's message to history
        history.append({"role": "user", "content": prompt})

        # Limit history size so the prompt doesn't grow forever.
        # 60 messages = ~30 turns (user+assistant).
        history[:] = history[-60:]

        # Call OpenAI Responses API with the full message list as input
        resp = client.responses.create(
            model=model,
            input=history,
        )

        # output_text is a convenience field for "best text answer"
        answer = resp.output_text.strip()

        # Print to terminal
        print(answer)
        print()

        # Save assistant reply back into history so the conversation continues
        history.append({"role": "assistant", "content": answer})
        save_history(history)


def main():
    """
    Entry point.

    - Validates that OPENAI_API_KEY exists
    - Determines prompt source
    - Handles --reset
    - Starts REPL if no prompt was provided and stdin is a TTY
    - Otherwise does one-shot call and prints result
    """
    # Read API key from environment variable.
    # We don't hardcode it in the file for safety.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='sk-...'", file=sys.stderr)
        sys.exit(1)

    # Allow model override via env var:
    #   OPENAI_MODEL="gpt-4.1-mini" chatgpt "hello"
    model = os.getenv("OPENAI_MODEL", MODEL_DEFAULT)

    # Figure out the user's input (args or stdin)
    prompt = get_prompt_from_args_or_stdin()

    # Special command: reset history file
    if prompt == "--reset":
        # missing_ok=True prevents error if file doesn't exist (Python 3.8+)
        HISTORY_PATH.unlink(missing_ok=True)
        print("History cleared.")
        return

    # Create OpenAI client (will read OPENAI_API_KEY automatically)
    client = OpenAI()

    # If no prompt and we are at a real terminal, start REPL
    if not prompt and sys.stdin.isatty():
        history = load_history()
        repl(client, history, model)
        return

    # If still no prompt here, that means stdin was empty too
    if not prompt:
        print("Usage:", file=sys.stderr)
        print('  chatgpt "Your question here"', file=sys.stderr)
        print("  chatgpt explain bfs", file=sys.stderr)
        print("  cat file.txt | chatgpt", file=sys.stderr)
        print("  chatgpt --reset", file=sys.stderr)
        sys.exit(2)

    # One-shot mode: load history, add user prompt, send, print answer, save
    history = load_history()
    history.append({"role": "user", "content": prompt})
    history = history[-60:]

    resp = client.responses.create(
        model=model,
        input=history,
    )

    answer = resp.output_text.strip()
    print(answer)

    history.append({"role": "assistant", "content": answer})
    save_history(history)


if __name__ == "__main__":
    # This makes the script runnable as:
    #   python3 chatgpt.py
    # or, if executable:
    #   ./chatgpt.py
    main()

