# 📚 AI Deadline Tracker

An AI-powered academic deadline tracker that extracts important
deadlines, exams, assignments, projects, and academic milestones
from uploaded academic documents using Gemini Vision.

The extracted deadlines are displayed in an organized table and
can also be sent to a student's email as a professional deadline
digest.

---

## 🚀 Features

- 📷 Upload syllabus, timetable, assignment sheet, or academic document
- 🤖 Extract academic deadlines using Gemini Vision
- 📅 Identify assignments, exams, quizzes, projects, readings, and milestones
- 📊 Display extracted deadlines in an organized table
- 📧 Send deadline digest through Gmail
- ✉️ Enter a different recipient email for each digest
- 🔐 Keep API keys and Gmail credentials in Streamlit Secrets
- 📓 Includes Jupyter Notebook used during development and testing

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Pillow
- Gmail SMTP
- Jupyter Notebook

---

## 📁 Project Structure


AI Deadline Tracker/
│
├── app.py
├── prompts.py
├── Deadline_Tracker.ipynb
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    ├── secrets.toml
    └── secrets.toml.example