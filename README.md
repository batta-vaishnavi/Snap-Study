# 📚 Snap & Study

Snap & Study is an AI-powered study assistant that helps students understand, revise, and prepare study material using Google's Gemini multimodal AI.

## ✨ Features

- 💬 Ask study-related questions
- 🖼️ Upload notes, textbook pages, questions, or diagrams
- 🤖 AI-powered image and text understanding
- 💡 Explain difficult concepts in simple language
- 📝 Generate concise exam-friendly notes
- ❓ Generate multiple-choice questions
- 🎯 Create exam-ready answers
- 📲 Generate study-session summaries and send them to Telegram
- ⚡ Quick study tools for faster revision

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- Telegram Bot API
- Requests

## 🏗️ Architecture

```text
Student
   ↓
Streamlit Interface
   ↓
Text / Image Input
   ↓
Google Gemini
   ↓
Study Assistance
   ├── Explain
   ├── Notes
   ├── Quiz
   └── Exam Answer
          ↓
   Study Summary
          ↓
   Telegram Bot