# 🏋️‍♂️ FitWell Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/backend-Flask-black.svg)](https://flask.palletsprojects.com/)
[![LangGraph](https://img.shields.io/badge/agent-LangGraph-orange.svg)](https://www.langchain.com/langgraph)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> A personalized, privacy-conscious AI fitness and wellness coach built with **LangGraph**, **Flask**, and **Vanilla Web Technologies**. FitWell translates health goals and metrics into dynamic, actionable routines and real-time guidance while keeping all user data strictly local.

---

## ✨ Features

- 🧠 **Autonomous ReAct Agent**: Built with **LangGraph** to dynamically reason, call tools, inspect past history, and generate context-aware fitness advice.
- 🔒 **Privacy-First Local Memory**: All user profiles, conversation history, workouts, meals, and body metrics reside in an atomic local `data/memory.json` file—zero external cloud database required.
- ⚡ **Dual LLM Provider Flexibility**:
  - **Local Ollama**: Run 100% locally and privately with models like `gemma4:e4b` or `llama3`.
  - **Google Gemini**: Switch seamlessly to cloud-based Gemini (e.g., `gemini-2.5-flash`) via `langchain-google-genai`.
- 📊 **Dynamic Dashboard & Analytics**:
  - Interactive chat interface with streaming feedback and tool-call indicators.
  - Workout logging with sets, reps, and progressive overload tracking.
  - Meal and macronutrient tracking (protein, carbs, fats, calories).
  - Bodyweight and cardio tracking with visual charts and metrics.
- 🗺️ **Spatial Facility Discovery**: Curated nearby gym, studio, and park discovery (offline mock dataset included with clean extensibility for live maps APIs).

---

## 🏛️ System Architecture

```text
               +-----------------------------+
               |  Modern Web UI (HTML/CSS/JS)|
               +--------------+--------------+
                              | REST / Fetch
                              v
               +-----------------------------+
               |      Flask Backend API      |
               |       (app/routes.py)       |
               +--------------+--------------+
                              |
               +--------------v--------------+
               |    LangGraph ReAct Agent    |
               |      (graph/agent.py)       |
               +-------+--------------+------+
                       |              |
         +-------------v----+   +-----v-------------+
         | Local Ollama LLM |   | Google Gemini API |
         |   (Offline AI)   |   |    (Cloud AI)     |
         +------------------+   +-------------------+
                       |
               +-------v---------------------+
               |   Local Atomic Data Store   |
               |     (data/memory.json)      |
               +-----------------------------+
```

---

## 🚀 Quickstart Guide

### Prerequisites

- **Python**: 3.10 or higher
- **Git**
- *(Optional)* **Ollama**: If running models locally ([ollama.com](https://ollama.com))

### 1. Clone the Repository

```bash
git clone https://github.com/devedroy/fit-well-agent.git
cd fit-well-agent
```

### 2. Set Up Virtual Environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the template configuration file:

```bash
cp .env.example .env
```

Open `.env` and set your preferred provider:

#### Option A: Local Ollama (Default, Free & Offline)
1. Ensure Ollama is running:
   ```bash
   ollama pull gemma4:e4b
   ollama serve
   ```
2. In your `.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=gemma4:e4b
   OLLAMA_BASE_URL=http://localhost:11434
   ```

#### Option B: Google Gemini Cloud
1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. In your `.env`:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

### 5. Seed Starter Data (Optional)

To populate sample profile and workout data for testing:

```bash
python -m database.seed_data
```

### 6. Run the Application

```bash
python run.py
```

Open your browser and navigate to:
👉 **[http://localhost:5001](http://localhost:5001)**

---

## ⚙️ Configuration Reference

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `ollama` | Provider selection: `ollama` or `gemini` |
| `OLLAMA_MODEL` | `gemma4:e4b` | Ollama model identifier |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama local server URL |
| `GEMINI_API_KEY` | - | Google Gemini API key (required if `LLM_PROVIDER=gemini`) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `USE_DUMMY_MAP_DATA`| `true` | Use bundled facility catalog without external API keys |
| `PORT` | `5001` | Local web server port |

---

## 📁 Repository Structure

```text
fit-well-agent/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Environment configuration loader
│   └── routes.py             # REST API routes and endpoints
├── database/
│   ├── db_manager.py         # Atomic read/write operations for local memory
│   ├── schema.sql            # Reference schema
│   └── seed_data.py          # Demo dataset seeder
├── data/
│   └── memory.json           # Local JSON database (user profile, history, logs)
├── graph/
│   ├── __init__.py
│   ├── agent.py              # LangGraph ReAct agent orchestration & fallback
│   ├── state.py              # Agent state definitions (TypedDict)
│   └── tools.py              # Tools: workout logger, meal tracker, facility search
├── static/
│   ├── css/style.css         # Modern glassmorphism stylesheet
│   ├── js/chat.js            # Chat messaging and UI logic
│   └── js/dashboard.js       # Dashboard cards, charts, and data interactions
├── templates/
│   └── index.html            # Main dashboard and chat view
├── specs/                    # Project specifications and architecture docs
├── .env.example              # Template environment variables
├── requirements.txt          # Python dependencies
├── run.py                    # Server startup script
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!

1. Check out the [Contributing Guidelines](CONTRIBUTING.md).
2. Adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).
3. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m 'feat: add amazing new feature'
   ```
5. Push to the branch and submit a Pull Request.

---

## 📜 License & Proper Attribution

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

### Attribution Requirement
Anyone is free to use, modify, distribute, or build upon this project for personal, educational, or commercial purposes, provided that **proper credit and attribution** are given to the original author:

> **FitWell Agent** by **Devpreyo Roy** ([@devedroy](https://github.com/devedroy))  
> Repository: [https://github.com/devedroy/fit-well-agent](https://github.com/devedroy/fit-well-agent)

When using this codebase in your own projects, please retain the copyright notice in the [LICENSE](LICENSE) file and provide a link back to this repository in your documentation or README.
