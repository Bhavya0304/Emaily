# 📬 Emaily — AI-Powered Email Categorizer

**Emaily** is an open-source project that automatically categorizes and organizes Gmail inboxes using real-time webhooks and Groq-hosted LLaMA 3 70B. It's built on a custom MVC backend in Python, uses a graph database for category relationships, and processes tasks asynchronously via Celery with RabbitMQ.

---

## 🧠 Features

- 🔐 Google OAuth for authentication
- 📥 Listens to incoming emails via Gmail Pub/Sub
- 🧠 Sends emails to Groq-hosted LLaMA 3 70B for intelligent classification
- 🗂️ Creates Gmail labels dynamically if needed
- 📤 Moves emails to matched folders automatically
- 📊 Stores user-defined categories in Neo4j
- 🧵 Uses Celery for background processing

---

## 💡 Tech Stack

| Layer             | Technology                     |
|------------------|--------------------------------|
| Backend          | Python (Flask + custom MVC)    |
| Task Queue       | Celery + RabbitMQ (Dockerized) |
| LLM              | Groq Cloud (LLaMA 3 70B)        |
| Database         | Neo4j (Graph DB)               |
| OAuth            | Google (Gmail only)            |
| Email API        | Gmail API + Pub/Sub Webhooks   |
| Frontend (TODO)  | Angular                        |
| Containerization | Docker                         |

---

## 📁 Project Structure

```
emaily/
├── app/
│   ├── controllers/       # Route handlers
│   ├── services/          # Business logic
│   ├── tasks/             # Celery workers
│   ├── models/            # Data and graph models
│   ├── llm/               # Groq integration
│   ├── config.py          # App configuration
│   └── app.py             # Flask entrypoint
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/emaily.git
cd emaily
```

### 2. Setup Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start RabbitMQ and Celery

```bash
docker-compose up -d  # starts RabbitMQ
celery -A app.tasks.worker worker --loglevel=info
```

### 4. Configure `.env`

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GMAIL_WEBHOOK_SECRET=
NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=
GROQ_API_KEY=
```

### 5. Run Flask App

```bash
python app.py
```

---

## ✅ Completed

- [x] Google OAuth login
- [x] Gmail webhook integration
- [x] LLM-based email classification (Groq)
- [x] Gmail folder creation and email sorting
- [x] Neo4j graph-based category persistence
- [x] Celery async task processing

---

## 🚧 TODO

- [ ] Angular frontend UI
- [ ] Outlook integration (Microsoft Graph API)
- [ ] Hosting and deployment pipeline
- [ ] Edge case handling and retries

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo, create issues, or submit PRs. Ideas, bugs, and improvements all help.

---

## 📄 License

GPL - 3.0 (Because I Love GNU)

---

## ✉️ Contact

For questions, ideas, or collaboration, feel free to reach out via GitHub.

---
