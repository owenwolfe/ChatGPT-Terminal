# ChatGPT Terminal

A simple, fast, and practical ChatGPT wrapper you can use directly from your terminal.

This tool lets you talk to ChatGPT without opening a browser. This is great for quick explanations, coding help, and staying in flow.

---

## Features

- Interactive REPL mode
- Prompts from the command line
- Input from stdin
- Persistent conversation memory
- Easy history reset
- No silent hangs

---

## Usage

### Interactive mode
-bash-
chatgpt
Example:

Welcome to the terminal of GPT (to quit -> 'exit')
> explain bfs
> now compare it to dfs
> exit

One-shot prompt:
-bash-
chatgpt explain bfs

Pipe input:
-bash-
cat notes.txt | chatgpt

Reset conversation history:
-bash-
chatgpt --reset

You can also reset inside the REPL:
> /reset

Installation:

1. Clone the repository
-bash-
git clone https://github.com/owenwolfe/ChatGPT-Terminal.git
cd ChatGPT-Terminal

3. Create a venv
-bash-
python3 -m venv .venv
source .venv/bin/activate

4. Install dependencies
-bash-
pip install openai

5. Set your OpenAI API key
-bash-
export OPENAI_API_KEY="sk-..."
To make this permanent, add it to ~/.zshrc or ~/.bashrc.

6. Make the script executable
-bash-
chmod +x chatgpt.py

8. Install as a global command
-bash-
sudo ln -sf "$(pwd)/chatgpt.py" /usr/local/bin/chatgpt

Verify:
-bash-
which chatgpt
Configuration
Model selection
By default, the wrapper uses:
gpt-4.1-mini

You can override it:
-bash-
OPENAI_MODEL="gpt-4.1" chatgpt explain dijkstra

Conversation history history is stored at:
-bash-
~/.chatgpt_history.json
History is automatically trimmed to avoid excessive token usage.

If you see a 429 Too Many Requests error, it usually means:
Your organization has hit its token-per-minute limit, or
billing/credits are not configured

Sometimes you just want to type:
-bash-
chatgpt explain this error
Without opening a browser or breaking focus.

This tool keeps ChatGPT where it’s most useful: your terminal.

License:
MIT License

Acknowledgements:
Built with help from ChatGPT (OpenAI).
