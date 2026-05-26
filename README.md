# ResuMatch — AI-Powered Job Matching System
### Built for "Build with AI" Hackathon · APU
Powered by **Chutes.ai** and **Morpheus (mor.org)**

---

## What it does
1. **Upload Resume** — Upload PDF, DOCX, or TXT. AI reads and extracts your profile.
2. **Profile Identified** — AI detects your major (Software Engineer, Designer, etc.), skills, level, and experience.
3. **Browse Jobs** — Fetches real jobs from LinkedIn/Indeed (via JSearch) and Malaysia-specific demo data for Jobstreet & RiceBowl.
4. **Match Analysis** — AI scores how well you match a job (0–100) with a breakdown by skills, experience, and education. Click "Full Report" for detailed advice.

---

## Project Structure

```
resumatch/
├── app.py                  ← Flask backend (resume parsing, job fetching, AI match)
├── requirements.txt        ← Python dependencies
├── templates/
│   └── index.html          ← Main UI (HTML)
├── static/
│   ├── css/style.css       ← All styling
│   └── js/app.js           ← Frontend logic
└── uploads/                ← Temp folder for resume uploads (auto-cleared)
```

---

## Setup & Run

### Step 1 — Open VS Code, open the `resumatch` folder

### Step 2 — Open terminal (Ctrl + `) and create virtual environment
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
If you get a red error about scripts being disabled:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then activate again.

### Step 3 — Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4 — Run the app
```powershell
python app.py
```

### Step 5 — Open browser
Go to: **http://127.0.0.1:5000**

---

## API Keys You Need

### 1. AI Engine Key (Required)
Pick ONE of these — paste it in the top bar of the app:

**Chutes.ai (recommended)**
- Go to https://chutes.ai
- Sign up → Settings → API Keys → Create
- Key starts with `cpk_...`

**Morpheus (mor.org)**
- Go to https://app.mor.org
- Sign up → API Keys → Generate
- Key starts with `sk-...`

### 2. RapidAPI Key (Optional — for real LinkedIn/Indeed jobs)
- Go to https://rapidapi.com
- Sign up (free)
- Search for **"JSearch"** by OpenWeb Ninja
- Subscribe to the free plan (100 requests/month)
- Copy your `x-rapidapi-key`
- Paste it in the "RapidAPI Key" field in the app

> Without this key, only Jobstreet and RiceBowl (demo data) will load.
> The demo data is realistic and works great for hackathon demos.

---

## How the AI Match Works
- **Score view** (default): Overall score 0–100, sub-scores for skills/experience/education, matched vs missing skills
- **Full Report** (click the button): Detailed AI-written analysis with strengths, gaps, recommendations, and interview tips

---

## Supported File Formats
| Format | Notes |
|--------|-------|
| PDF    | Best support — use text-based PDFs, not scanned images |
| DOCX   | Microsoft Word documents |
| TXT    | Plain text resumes |

---

## Notes for Hackathon Demo
- Data resets on server restart (in-memory). Fine for demo.
- Jobstreet & RiceBowl use realistic mock data (their APIs are not publicly available).
- LinkedIn, Indeed, Glassdoor use real live data via JSearch (RapidAPI free tier).
- You can switch between Chutes.ai and Morpheus engines at any time using the toggle in the top bar.
