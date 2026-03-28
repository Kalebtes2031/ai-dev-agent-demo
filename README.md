# 🤖 AI-Dev-Agent: Your Autonomous GitHub coding assistant

[![Replit](https://img.shields.io/badge/Deployed%20on-Replit-blue?logo=replit&logoColor=white)](https://ai-dev-agent-demo--kalebayele2001.replit.app)
[![OpenAI](https://img.shields.io/badge/Powered%20by-GPT--4o-green?logo=openai&logoColor=white)](https://openai.com/)
[![Telegram](https://img.shields.io/badge/Interface-Telegram-blue?logo=telegram&logoColor=white)](https://t.me/GithubAssistancebot)

An advanced, autonomous AI developer that lives in your Telegram. Describe your project idea in natural language, and AI-Dev-Agent will architect the project, write the code, and push it directly to your GitHub repository via secure SSH.

---

## 🚀 Key Features

- **⚡ Instant Scaffolding**: Create full React, Vite, Python, or Node.js projects with a single message.
- **🤖 Agentic Workflow**: Uses OpenAI's **GPT-4o** with a multi-turn tool-calling loop (up to 20 turns) to chain file creation and Git operations autonomously.
- **🔒 Secure SSH Integration**: Robust SSH key reconstruction logic for safe, automated GitHub authentication on cloud platforms like Replit and Render.
- **🧠 Stateful Conversations**: Remembers your project context, allowing for iterative development ("Now add a database layer," "Refactor the main component").
- **🐳 Cloud-Ready**: Includes full `Dockerfile` and `render.yaml` for one-click deployment.

---

## 🏗️ Architecture

AI-Dev-Agent follows a clean, decoupled architecture:

- **`bot/`**: Telegram interface layer using `python-telegram-bot` for reliable, asynchronous communication.
- **`agent/`**: The "Brain" of the operation. Orchestrates OpenAI tool-calling and manages conversational state.
- **`executor/`**: The "Hands" of the system. Handles the physical file system operations and Git commands.
- **`projects/`**: Sandbox directory where AI projects are built before being pushed to GitHub.

---

## 🛠️ Setup & Deployment

### 1. Environment Variables
Create a `.env` file (or set these in your Cloud Provider's Secrets):

```env
TELEGRAM_BOT_TOKEN=your_telegram_token
OPENAI_API_KEY=your_openai_key
GITHUB_SSH_PRIVATE_KEY=your_ssh_key_blob
GITHUB_USERNAME=your_username
GITHUB_SSH_ALIAS=github-mekonnen (optional)
PROJECTS_ROOT=ai_dev_agent/projects
```

### 2. Deploying on Replit
1. Import your repository into Replit.
2. Add your secrets via the **Tools > Secrets** tab.
3. Replit will automatically detect the `Dockerfile` or use the `start.sh` entry point.

### 3. Deploying on Render
1. Use the included `render.yaml` to deploy as a **Background Worker**.
2. Mount your `GITHUB_SSH_PRIVATE_KEY` as a **Secret File** or Environment Variable.

---

## 💬 How to Use

1. Start a conversation with [GithubAssistancebot](https://t.me/GithubAssistancebot).
2. Use the `/start` command to initialize.
3. Send a prompt like: 
   > *"I want to create a simple React/Vite project called 'weather-dashboard' that shows current weather for a city using a public API."*
4. Watch as the AI architects your project, creates the files, and pushes the code to your GitHub!

---

## 📜 License & Author

Crafted by **Kaleb Tesfaye**.
Licensed under the [MIT License](LICENSE).
