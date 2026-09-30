# 📚 AI Deadline Tracker

An AI-powered academic deadline tracker that extracts important
deadlines from academic documents using Google Gemini Vision and
sends the extracted deadline information through email.

## ✨ Features

- 📷 Upload academic documents
- 🤖 Extract deadlines using Gemini Vision
- 📅 Display deadlines in an organized table
- 📧 Send deadline digest through Gmail
- 🔐 Secure API key and email credentials using Streamlit Secrets
- 📓 Includes Jupyter Notebook for development and testing

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Google GenAI SDK
- Pillow
- Gmail SMTP
- Jupyter Notebook

## 📁 Project Structure

```text
AI Deadline Tracker/
│
├── app.py
├── prompts.py
├── Deadline_Tracker.ipynb
├── requirements.txt
├── README.md
├── .gitignore
│
├── test_images/
│   ├── test1_syllabus.png
│   ├── test2_timetable.png
│   └── test3_no_deadline.png
│
└── .streamlit/
    ├── secrets.toml
    └── secrets.toml.example
