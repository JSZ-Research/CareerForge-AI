# CareerForge AI: Professional Career Suite 🚀

**The Ultimate AI Career Copilot powered by Google Gemini 3 Pro.**

[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io) [![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Google%20GenAI-4285F4.svg)](https://deepmind.google/technologies/gemini/) [![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg)](https://python.org)

**CareerForge AI** is an all-in-one desktop application designed to give job seekers an unfair advantage. It combines **computer vision**, **multimodal LLMs**, and **agentic workflows** to simulate a real career coach sitting right next to you.

---
## 🎥 Live Demo

[![Career Forge AI Demo](https://img.youtube.com/vi/yqUrn0oUv18/0.jpg)](https://youtu.be/yqUrn0oUv18)

---

## 🔥 Key Features

### 1. 🎥 AI Video Interview Coach (Hackathon Highlight)
*   **Real-time Eye Contact & Expression Analysis**: Uses **MediaPipe Face Mesh** to track your facial cues (micro-expressions, eye contact percentage) in real-time as you speak.
*   **Multimodal Feedback**: **Gemini 3 Pro** watches your video and listens to your audio to provide a second-by-second timeline analysis of your confidence, tone, and answer quality.
*   **Mock Interview Loop**:
    *   **Dynamic Question Generation**: AI reads the specific Job Description (JD) and generates 3 tailored interview questions (Icebreaker, Behavioral, Situational).
    *   **Sequential Flow**: Simulate a real interview round-by-round with privacy-focused auto-clearing between questions.
    *   **Voice Interviewer (TTS)**: The AI reads questions aloud to feel like a real conversation.

### 2. 📝 Smart Resume Review
*   **ATS Simulation**: uploading your Resume (PDF) and the Target JD gives you an instant **Match Score (0-100%)**.
*   **Deep Analysis**: Identifies critical keyword gaps, highlights strengths, and offers concrete improvement suggestions.
*   **Persistent Context**: Resume data is synchronized across the app—upload once, and use it for Cover Letters or Interview Coaching.

### 3. ✍️ Tailored Cover Letter Generator
*   **One-Click Generation**: Creates hyper-personalized cover letters that weave your specific skills into the company's requirements.
*   **Model Agnostic**: Supports both **Google Gemini** (Recommended) and **OpenAI GPT-4o**.
*   **Pro Exports**: Download as polished PDF, Word (.docx), or LaTeX (.tex).

### 4. 🔒 Privacy & Security Vault
*   **Local-First Architecture**: Your data lives on your machine.
*   **Encrypted Secrets**: Built-in vault to encrypt your API keys with a master password (AES-256).

---

## 🛠️ Tech Stack

*   **Core**: Python, Streamlit
*   **AI Models**: Google Gemini 3.0 Pro (Multimodal) / 2.0 Flash
*   **Computer Vision**: Google MediaPipe (Face Landmarker)
*   **Communication**: WebRTC (`streamlit-webrtc`) for real-time video streaming
*   **Audio**: gTTS (Google Text-to-Speech)

---

## 🚀 Quick Start

### Prerequisites
*   Python 3.10+
*   Google Gemini API Key (Get it [here](https://aistudio.google.com/))

### Installation

1.  **Clone the Repo**
    ```bash
    git clone https://github.com/JSZ-Research/CareerForge-AI.git
    cd CareerForge-AI
    ```

2.  **Setup & Run**

    **🍏 macOS / Linux**:
    ```bash
    ./setup.sh
    ./start_app.command
    ```

    **🪟 Windows**:
    Double-click `setup.bat` first (to install), then double-click `start_app.bat` to launch. 


---
## 👥 Team & Contributions

This project was developed under the **JSZ-Research** GitHub organization for the Google Gemini Developer Competition.

*   **Hanson He** ([@HansonHe](https://github.com/HansonHe-UW))  
    *Primary Architect & Lead Developer.* Responsible for the core engine, multimodal integration, and the implementation of the AI Video Interview Coach.
*   **Jiamu Shangguan** ([@JiamuShangguan](https://github.com/mu142857)), **Kaius Jin** ([@KaiusJin](https://github.com/KaiusJin)), **Junkai Zhao** ([@JunkaiZhao](https://github.com/anoyume91))  
    *Strategy & Product Advisors.* Contributed critical product feedback, UI/UX optimization suggestions, and feature roadmap planning.

## 📸 Screenshots

| Interview Coach | Resume Review |
|:---:|:---:|
| *(Placeholders for demo screenshots)* | *(Placeholders for demo screenshots)* |

---

## 📄 License
MIT License. Built for the Google Gemini Developer Competition.
