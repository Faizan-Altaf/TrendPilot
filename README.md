# TrendPilot — Agentic AI Content Planning Agent

TrendPilot is a local-LLM content planning assistant built for the AIRI Team PITB AI Internship Task 2.

## Features
- Content ideas, captions, hashtags, short-video scripts, titles, and thumbnail wording
- Structured JSON output, validation, and one repair attempt
- Optional content review
- File Saver for TXT, Markdown, and JSON
- Persistent SQLite task memory
- Local Streamlit interface using Ollama
- Automated checks and a five-output batch workflow

## Stack
Python, Ollama, Qwen 2.5 3B, SQLite, Streamlit, JSON, Markdown.

## Setup
1. Install Ollama from https://ollama.com/.
2. Download the model: `ollama pull qwen2.5:3b`
3. Install packages: `python -m pip install ollama streamlit`
4. Open `TrendPilot_Updated.ipynb` in VS Code and run cells in order.
5. Run the Streamlit app using the command printed by the notebook.

## Agent workflow
Receive topic/audience/platform -> validate inputs -> generate structured plan -> validate JSON -> optionally repair/review -> save JSON and Markdown -> store task in SQLite -> return result.

## Output and memory
Content plans are saved in `outputs/`. Task history is stored in `data/trendpilot_memory.db`.

## Limitations
TrendPilot does not verify live trends. Model outputs can be inaccurate or repetitive and should be reviewed. The Streamlit interface runs locally and requires Ollama to be available on the same computer.

## Testing
Run the notebook's automated test cell. Report the actual pass/fail results rather than assuming tests passed. Run the five-output batch separately; it makes five model calls.
