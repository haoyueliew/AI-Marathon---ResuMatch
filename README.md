# ResuMatch — AI-Powered Job Matching System

> Upload your resume. Get matched to jobs instantly using Morpheus AI.

Built for the **Build with AI Hackathon (AI Marathon)** · Powered by **Morpheus AI (LLaMA 3.3-70B)**

---

## Problem Statement

Job seekers in Malaysia spend hours manually comparing their resumes to job listings without knowing if they are a good match before applying. This leads to wasted time, low response rates, and frustration. ResuMatch solves this by using AI to instantly analyse a candidate's resume, extract their profile, and score how well they match any job listing — giving users actionable insights before they even click apply.

---

## Project Structure

```
AIC AI Marathon/
├── app.py                  # Flask backend + Morpheus AI agent logic
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── uploads/                # Temporary upload folder (auto-created)
├── templates/
│   └── index.html          # Main frontend UI
└── static/
    ├── css/
    │   └── style.css       # Styling
    └── js/
        └── app.js          # Frontend logic
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python 3.12, Flask |
| AI Engine | Morpheus AI — LLaMA 3.3-70B |
| PDF Parsing | PyMuPDF, pdfplumber |
| DOCX Parsing | python-docx |

---

## User Manual

### Setup Instructions

#### Requirements
- Python 3.10 or newer
- VS Code
- Windows (PowerShell)

---

#### Step 1 — Download and unzip the project

1. Download the project file `AIC_AI_Marathon.zip`
2. Right-click the ZIP file → **Extract All** → choose your destination folder

---

#### Step 2 — Open project in VS Code

1. Open VS Code
2. Click **File** → **Open Folder**
3. Select the `AIC AI Marathon` folder

---

#### Step 3 — Open terminal

1. On the top menu bar, click **Terminal**
2. Click **New Terminal**

---

#### Step 4 — Allow script execution (one-time setup only)

Run this command to allow PowerShell scripts to run on your PC:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

#### Step 5 — Create a virtual environment

```bash
python -m venv venv
```

---

#### Step 6 — Activate the virtual environment

```bash
venv\Scripts\Activate.ps1
```

You will see `(venv)` appear at the start of your terminal line — this means it worked:

```
(venv) PS C:\Users\YourName\...\AIC AI Marathon>
```

> **Important:** Every time you close and reopen VS Code, you must run this activate command again before starting the app.

---

#### Step 7 — Install required libraries

```bash
pip install -r requirements.txt
```

This downloads and installs all the Python packages the app needs (Flask, PyMuPDF, pdfplumber, etc.). Wait until it finishes — it may take 1–2 minutes.

---

#### Step 8 — Run the app

```bash
python app.py
```

You should see this output in the terminal:

```
====================================================
  ResuMatch — AI-Powered Job Matching System
  Powered by Morpheus AI (mor.org)
  http://127.0.0.1:5000
====================================================
```

---

#### Step 9 — Open in browser

Open your web browser and go to:

```
http://127.0.0.1:5000
```

Or hold **Ctrl** and click `http://127.0.0.1:5000` directly in the VS Code terminal.

---

### How to Use ResuMatch

#### Step 1 — Upload your resume

- Drag and drop your resume into the upload box, or click to browse
- Supported formats: PDF, DOCX, TXT (max 5 MB)
- Click **Analyse Resume** and wait 10–20 seconds for the AI to process it

#### Step 2 — Review your profile and search for jobs

- Your AI-extracted profile (name, skills, experience, education) will appear on the left
- Select your preferred job platforms (Jobstreet, RiceBowl)
- Adjust the job keywords if needed
- Click **Search Jobs**

#### Step 3 — Browse job listings

- A list of matched job listings will appear
- Jobs are ranked by relevance to your profile and keywords
- Click **Analyse Match** on any job card to check your compatibility

#### Step 4 — View your match analysis

- **Score view** — see your overall match score (0–100) with a breakdown across Skills, Experience, and Education, plus a list of matched and missing skills
- **Full Report** — click to get a detailed AI career coaching report covering your strengths, skill gaps, recommendations, and likely interview questions for that role

---

## Team

| Name | 
|---|
| [Liew Hao Yue] |
| [Low Ke Sin] | 
| [Thor Xiwen] | 