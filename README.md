# 🤖 AI Job Checker — AIC AI Marathon

> An AI-powered resume analysis and job matching web application that helps users find jobs aligned with their skills and experience.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Dependencies](#dependencies)
- [Project Structure](#project-structure)
- [Configuration & Setup](#configuration--setup)
- [Running the Application](#running-the-application)
- [How to Use](#how-to-use)
- [Troubleshooting](#troubleshooting)

---

## Overview

AI Job Checker is a Flask-based web application developed for the AIC AI Marathon Hackathon. It allows users to upload their resume (PDF), automatically extracts key information using AI, searches for matching job listings across multiple platforms, and generates a detailed compatibility report for each job.

### Problem Statement

![problem_statement.png](images/problem_statement.png)

### Project Structure Overview

![project_structure.png](images/project_structure.png)

---

## Features

- 📄 **Resume Upload & Parsing** — Drag-and-drop PDF upload with automatic text extraction
- 🔍 **Multi-Platform Job Search** — Search across multiple job platforms simultaneously
- 🧠 **AI-Powered Match Analysis** — Get a detailed compatibility report between your resume and any job listing
- 📊 **Match Score Report** — Visual breakdown of skill alignment, experience fit, and recommendations

---

## System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| **Operating System** | Windows 10, macOS 10.15, Ubuntu 20.04 | Windows 11 / macOS 13+ / Ubuntu 22.04 |
| **Python Version** | 3.10 | 3.11 or 3.12 |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 500 MB free | 1 GB free |
| **Internet Connection** | Required (for job search APIs) | Stable broadband |
| **Browser** | Chrome 90+, Firefox 88+, Edge 90+ | Latest Chrome or Firefox |

> **Note:** This application is primarily developed and tested on **Windows** using PowerShell. macOS/Linux users should refer to the [platform-specific activation commands](#platform-specific-activation) below.

---

## Dependencies

All dependencies are listed in `requirements.txt`. Key packages include:

| Package | Purpose |
|---|---|
| `Flask` | Web framework for the backend server |
| `pdfplumber` | PDF text extraction from uploaded resumes |
| `requests` | HTTP requests to external job listing APIs |
| `python-dotenv` | Loading environment variables from `.env` file |
| `openai` / `anthropic` *(if applicable)* | AI model integration for match analysis |

To view the full list of pinned versions, see [`requirements.txt`](./requirements.txt).

---

## Project Structure

```
AIC AI Marathon/
├── app.py                  # Main Flask application entry point
├── requirements.txt        # Python package dependencies
├── .env.example            # Example environment variable configuration
├── README.md               # This file
│
├── templates/              # HTML templates (Jinja2)
│   ├── index.html          # Page 1: Resume upload
│   ├── platforms.html      # Page 2: Platform selection
│   ├── jobs.html           # Page 3: Job listings
│   └── report.html         # Page 4–5: Match analysis report
│
├── static/                 # Static assets
│   ├── css/
│   ├── js/
│   └── images/
│
└── utils/                  # Helper modules
    ├── resume_parser.py    # PDF parsing logic
    ├── job_scraper.py      # Job search integration
    └── ai_matcher.py       # AI match analysis logic
```

---

## Configuration & Setup

### Step 1: Download and Extract the Project

1. Download `AIC_AI_Marathon.zip`
2. Right-click the ZIP file → **Extract All** → choose your target folder

### Step 2: Open the Project in VS Code

1. Open **Visual Studio Code**
2. Click **File → Open Folder**
3. Select the extracted `AIC AI Marathon` folder

### Step 3: Open a Terminal

In VS Code: click **Terminal** (top menu) → **New Terminal**

### Step 4: Allow Script Execution *(Windows — one-time setup)*

Run the following command to allow PowerShell scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 5: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 6: Activate the Virtual Environment

<a name="platform-specific-activation"></a>

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt:
```
(venv) PS C:\Users\YourName\...\AIC AI Marathon>
```

> ⚠️ **Important:** Every time you close and reopen VS Code, you must re-run the activation command above before starting the app.

### Step 7: Install Required Libraries

```bash
pip install -r requirements.txt
```

This may take 1–2 minutes. Wait until the installation completes fully.

### Step 8: Configure Environment Variables *(if applicable)*

If the project requires API keys (e.g., for AI model access or job search APIs):

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the required values:
   ```env
   OPENAI_API_KEY=your_key_here
   JOB_API_KEY=your_key_here
   ```

> If no `.env.example` exists, check with your team whether API keys are required.

---

## Running the Application

```bash
python app.py
```

Expected terminal output:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

Then open your browser and navigate to:

```
http://127.0.0.1:5000
```

> You can also **Ctrl + Click** the URL directly in the VS Code terminal.

To stop the server, press **Ctrl + C** in the terminal.

---

## How to Use

### Page 1 — Upload Resume

![page1.png](images/page1.png)

- Drag and drop your **PDF resume** into the upload box, or click to browse
- Press **"Analyse Resume"** to extract your skills and experience

### Page 2 — Select Job Platforms

![page2.png](images/page2.png)

- Choose one or more job platforms to search (e.g., LinkedIn, JobStreet, Indeed)
- Press **"Search Jobs"** to proceed

### Page 3 — Browse Job Listings

![page3.png](images/page3.png)

- View the list of matching job postings retrieved from your selected platforms
- Press **"Analyse Match"** on any job to generate a compatibility report

### Page 4–5 — Match Report

![page4.png](images/page4.png)

![page5.png](images/page5.png)

- Review your **match score** and a full breakdown of:
  - Skill alignment
  - Experience fit
  - Missing qualifications
  - Recommendations for improvement

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `python` not recognised | Ensure Python 3.10+ is installed and added to PATH |
| `venv\Scripts\Activate.ps1` error | Run the `Set-ExecutionPolicy` command in Step 4 |
| `ModuleNotFoundError` | Ensure virtual environment is active, then re-run `pip install -r requirements.txt` |
| Port 5000 already in use | Stop other Flask apps, or change the port in `app.py` with `app.run(port=5001)` |
| PDF not parsing correctly | Ensure the resume is a text-based PDF (not a scanned image) |
| No jobs returned | Check your internet connection and verify any required API keys in `.env` |

---

## Built With

- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF parsing
- [Python 3.10+](https://www.python.org/)

---

*Developed for the AIC AI Marathon Hackathon.*
