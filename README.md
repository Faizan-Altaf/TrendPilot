# TrendPilot AI 🚀

**An AI-powered content planning agent built with Python, Ollama, Qwen 2.5 3B, and Streamlit.**

TrendPilot helps turn different topics into structured content plans, ideas, captions, hashtags, short-form video scripts, titles, thumbnail text, and content-improvement suggestions.

The application runs locally using Ollama and provides a Streamlit interface.

## ✨ Features

- AI-powered content planning for different topics and audiences
- Content ideas and audience-focused hooks
- Reel and short-video scripts with scenes and voice-over text
- Captions and hashtags
- Titles and thumbnail text
- Optional web research for topics that need supporting information
- Persistent memory and history using SQLite
- Save generated content in JSON, Markdown, and TXT formats
- Streamlit user interface
- Local language-model inference through Ollama

## 🛠️ Tech Stack

- Python
- Ollama
- Qwen 2.5 3B
- Streamlit
- SQLite
- Requests and BeautifulSoup
- JSON, Markdown, and TXT

## 🧠 How It Works

1. Enter a topic or content goal.
2. Select the target audience, platform, tone, and content mode.
3. Search for relevant web results when research is needed and available.
4. Generate content using the local language model.
5. Review the generated ideas, scripts, captions, and suggestions.
6. Save and revisit results using the application's memory and export features.

## 📁 Project Structure

```text
TrendPilot/
├── app/
│   ├── agent.py
│   ├── main.py
│   ├── memory.py
│   ├── prompts.py
│   ├── streamlit_app.py
│   └── tools.py
├── data/
├── outputs/
├── report/
├── tests/
├── README.md
├── requirements.txt
├── test_app.py
└── TrendPilot_Updated (3).ipynb
```

## ⚙️ Requirements

- Python
- Ollama
- The Qwen 2.5 3B model
- Project dependencies listed in `requirements.txt`

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Faizan-Altaf/TrendPilot.git
cd TrendPilot
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Download the model

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running before launching the application.

### 5. Run the Streamlit app

```bash
python -m streamlit run app/streamlit_app.py
```

Open the local URL displayed in the terminal.

## 💾 Memory and File Saving

TrendPilot uses SQLite for persistent memory and can save generated content in supported export formats. Saved files and database locations depend on the application configuration.

## 🧪 Testing

Run the project's tests with:

```bash
python -m pytest -q
```

Test different topics, audiences, platforms, and content modes. Also check file exports, stored history, and behavior when web research is unavailable.

## ⚠️ Limitations

- Output quality depends on the local model and prompt.
- Generation speed depends on available hardware and model configuration.
- Web research depends on internet access and search availability.
- Search snippets are not the same as fully verified research.
- Generated facts and recommendations should be checked before publication.

## 🔮 Future Improvements

- Add a dedicated AI review and quality-scoring stage.
- Improve source retrieval and verification.
- Expand automated tests and failure handling.
- Optimize generation speed.
- Add more content templates and platform-specific workflows.

## 👨‍💻 Project Information

**Project:** TrendPilot AI  
**Developer:** Faizan Altaf  
**Repository:** https://github.com/Faizan-Altaf/TrendPilot

TrendPilot explores local LLMs, agentic workflows, tool use, persistent memory, and AI-assisted content planning.
