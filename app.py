import os
import re
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ── PDF / DOCX parsing ───────────────────────────────────────────────────────
try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    from docx import Document as DocxDocument
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Morpheus AI config ───────────────────────────────────────────────────────
MORPHEUS_API_KEY = "sk-vGXoYa.8b480741fc8bb38b1680c9a6ce0d0f6a7f10faad6bb3967be3b799ad5e54c08d"
MORPHEUS_URL     = "https://api.mor.org/api/v1/chat/completions"
MORPHEUS_MODELS  = ["llama3.3-70b", "llama-3-70b", "llama3-70b"]

# ── Mock jobs (demo data only — all platforms) ────────────────────────────────
MOCK_JOBS = {
    "jobstreet": [
        {"id":"js1","platform":"Jobstreet","title":"Software Engineer (Backend)","company":"Grab","location":"Kuala Lumpur","type":"Full-time","salary":"RM 6,000 – RM 10,000","posted":"2 days ago","url":"https://my.jobstreet.com","description":"Design and build scalable backend services using Python and Go. Work with distributed systems, Kafka, PostgreSQL, and AWS. Strong understanding of microservices, REST APIs and cloud-native architecture required.","skills":["Python","Go","Kafka","PostgreSQL","AWS","REST APIs","Docker","Microservices"]},
        {"id":"js2","platform":"Jobstreet","title":"Frontend Developer (React)","company":"Shopee","location":"Petaling Jaya","type":"Full-time","salary":"RM 5,000 – RM 8,000","posted":"1 day ago","url":"https://my.jobstreet.com","description":"Build fast, accessible, and responsive user interfaces using React and TypeScript. Collaborate with designers and backend engineers to deliver world-class products.","skills":["React","TypeScript","CSS","HTML","JavaScript","GraphQL","Git","Jest"]},
        {"id":"js3","platform":"Jobstreet","title":"Data Scientist","company":"CIMB Bank","location":"Kuala Lumpur","type":"Full-time","salary":"RM 7,000 – RM 12,000","posted":"3 days ago","url":"https://my.jobstreet.com","description":"Develop predictive models for credit risk and customer churn using Python and TensorFlow. Experience with SQL and data pipelines required.","skills":["Python","Machine Learning","SQL","TensorFlow","scikit-learn","Data Analysis","Statistics","Pandas"]},
        {"id":"js4","platform":"Jobstreet","title":"UX/UI Designer","company":"AirAsia","location":"Sepang","type":"Full-time","salary":"RM 4,500 – RM 7,000","posted":"5 days ago","url":"https://my.jobstreet.com","description":"Design intuitive digital experiences for millions of travellers. Proficiency in Figma, user research, design systems and prototyping required. Portfolio required.","skills":["Figma","UI Design","UX Research","Prototyping","Design Systems","Adobe XD","User Testing","Wireframing"]},
        {"id":"js5","platform":"Jobstreet","title":"DevOps Engineer","company":"Axiata","location":"Kuala Lumpur","type":"Full-time","salary":"RM 6,500 – RM 11,000","posted":"1 day ago","url":"https://my.jobstreet.com","description":"Manage and scale cloud infrastructure on AWS. Implement CI/CD pipelines, Kubernetes clusters, and IaC using Terraform. Strong Linux and scripting skills needed.","skills":["AWS","Kubernetes","Terraform","Docker","CI/CD","Linux","Python","Bash"]},
        {"id":"js6","platform":"Jobstreet","title":"Digital Marketing Executive","company":"Lazada","location":"Kuala Lumpur","type":"Full-time","salary":"RM 3,500 – RM 5,500","posted":"4 days ago","url":"https://my.jobstreet.com","description":"Plan and execute digital marketing campaigns across social media and SEM. Analyse performance data and optimise ROI. Google Ads and Meta Ads experience required.","skills":["Digital Marketing","Google Ads","Meta Ads","SEO","Content Marketing","Analytics","Social Media","Copywriting"]},
        {"id":"js7","platform":"Jobstreet","title":"Mobile Developer (Android)","company":"Maybank","location":"Kuala Lumpur","type":"Full-time","salary":"RM 5,500 – RM 9,000","posted":"Today","url":"https://my.jobstreet.com","description":"Develop and maintain Android applications for banking services. Kotlin and Jetpack Compose required. Experience with REST APIs and secure mobile development preferred.","skills":["Android","Kotlin","Jetpack Compose","REST APIs","Git","Java","Firebase","Agile"]},
        {"id":"js8","platform":"Jobstreet","title":"Business Analyst","company":"PwC Malaysia","location":"Kuala Lumpur","type":"Full-time","salary":"RM 5,000 – RM 8,500","posted":"2 days ago","url":"https://my.jobstreet.com","description":"Analyse business processes, gather requirements, and produce functional specifications. Work closely with stakeholders and development teams to deliver technology solutions.","skills":["Business Analysis","Requirements Gathering","SQL","Excel","Stakeholder Management","Agile","JIRA","Documentation"]},
        {"id":"js9","platform":"Jobstreet","title":"Network Engineer","company":"TM","location":"Kuala Lumpur","type":"Full-time","salary":"RM 4,500 – RM 7,500","posted":"3 days ago","url":"https://my.jobstreet.com","description":"Design, implement and maintain enterprise network infrastructure. Experience with Cisco routers, firewalls, VPN, and network monitoring tools required.","skills":["Networking","Cisco","Firewall","VPN","Linux","TCP/IP","Network Monitoring","CCNA"]},
        {"id":"js10","platform":"Jobstreet","title":"Accountant","company":"Ernst & Young","location":"Kuala Lumpur","type":"Full-time","salary":"RM 4,000 – RM 7,000","posted":"4 days ago","url":"https://my.jobstreet.com","description":"Prepare financial statements, manage accounts payable/receivable, and support auditing processes. ACCA or CPA qualification required. Proficiency in SAP and Excel essential.","skills":["Accounting","Financial Reporting","SAP","Excel","Auditing","ACCA","Tax","Bookkeeping"]},
        {"id":"js11","platform":"Jobstreet","title":"HR Executive","company":"Sunway Group","location":"Petaling Jaya","type":"Full-time","salary":"RM 3,500 – RM 5,500","posted":"1 day ago","url":"https://my.jobstreet.com","description":"Manage recruitment, onboarding, payroll, and employee relations. Experience with HR systems and Malaysian labour law required.","skills":["Recruitment","Payroll","Employee Relations","HR Systems","Labour Law","Onboarding","Microsoft Office","Communication"]},
        {"id":"js12","platform":"Jobstreet","title":"Mechanical Engineer","company":"Petronas","location":"Kuala Lumpur","type":"Full-time","salary":"RM 5,000 – RM 9,000","posted":"5 days ago","url":"https://my.jobstreet.com","description":"Design and maintain mechanical systems for oil and gas facilities. Experience with AutoCAD, piping design, and pressure vessel calculations required.","skills":["AutoCAD","Mechanical Design","Piping","Pressure Vessel","SolidWorks","Engineering Drawings","Oil & Gas","Maintenance"]},
    ],
    "ricebowl": [
        {"id":"rb1","platform":"RiceBowl","title":"Full Stack Developer","company":"Fusionex","location":"Kuala Lumpur","type":"Full-time","salary":"RM 5,500 – RM 9,000","posted":"Today","url":"https://ricebowl.my","description":"Build end-to-end web applications using React and Node.js. Work with MongoDB and PostgreSQL in an Agile environment.","skills":["React","Node.js","MongoDB","PostgreSQL","REST APIs","Docker","JavaScript","Agile"]},
        {"id":"rb2","platform":"RiceBowl","title":"AI/ML Engineer","company":"Telekom Malaysia","location":"Kuala Lumpur","type":"Full-time","salary":"RM 8,000 – RM 14,000","posted":"2 days ago","url":"https://ricebowl.my","description":"Research and deploy machine learning models for network optimisation and anomaly detection. PyTorch and MLflow experience essential.","skills":["Python","PyTorch","MLflow","Machine Learning","NLP","AWS","Statistics","Deep Learning"]},
        {"id":"rb3","platform":"RiceBowl","title":"Graphic Designer","company":"Leo Burnett","location":"Petaling Jaya","type":"Full-time","salary":"RM 3,000 – RM 5,000","posted":"3 days ago","url":"https://ricebowl.my","description":"Create visual assets for print and digital campaigns. Proficiency in Adobe Creative Suite required. Strong portfolio of brand and advertising work expected.","skills":["Adobe Illustrator","Photoshop","InDesign","Branding","Typography","Print Design","Digital Design","Figma"]},
        {"id":"rb4","platform":"RiceBowl","title":"Cybersecurity Analyst","company":"Maybank","location":"Kuala Lumpur","type":"Full-time","salary":"RM 6,000 – RM 10,000","posted":"1 day ago","url":"https://ricebowl.my","description":"Monitor and respond to security incidents. Conduct vulnerability assessments and penetration testing. CISSP or CEH certification preferred.","skills":["Cybersecurity","Penetration Testing","SIEM","Vulnerability Assessment","Networking","Python","Linux","Incident Response"]},
        {"id":"rb5","platform":"RiceBowl","title":"Product Manager","company":"PropertyGuru","location":"Kuala Lumpur","type":"Full-time","salary":"RM 7,000 – RM 13,000","posted":"5 days ago","url":"https://ricebowl.my","description":"Lead product discovery and delivery for marketplace features. Define roadmap, write PRDs, and collaborate with engineering and design teams.","skills":["Product Management","Agile","User Research","Data Analysis","Roadmapping","Stakeholder Management","SQL","JIRA"]},
        {"id":"rb6","platform":"RiceBowl","title":"Cloud Architect","company":"MDEC","location":"Putrajaya","type":"Full-time","salary":"RM 10,000 – RM 18,000","posted":"Today","url":"https://ricebowl.my","description":"Design and oversee cloud infrastructure strategy for government digital transformation projects. AWS or Azure certification required.","skills":["AWS","Azure","Cloud Architecture","Terraform","Kubernetes","Security","Networking","Solution Design"]},
        {"id":"rb7","platform":"RiceBowl","title":"Content Writer","company":"iProperty","location":"Remote","type":"Full-time","salary":"RM 3,000 – RM 4,500","posted":"2 days ago","url":"https://ricebowl.my","description":"Write engaging property articles, landing pages, and marketing copy. Strong command of English and SEO writing skills required.","skills":["Copywriting","SEO","Content Marketing","WordPress","Research","Editing","Social Media","English"]},
        {"id":"rb8","platform":"RiceBowl","title":"Data Analyst","company":"AirAsia","location":"Kuala Lumpur","type":"Full-time","salary":"RM 4,500 – RM 7,500","posted":"3 days ago","url":"https://ricebowl.my","description":"Analyse large datasets to derive business insights. Create dashboards using Power BI and Tableau. SQL proficiency and Python for data wrangling required.","skills":["SQL","Python","Power BI","Tableau","Excel","Data Visualisation","Statistics","Pandas"]},
        {"id":"rb9","platform":"RiceBowl","title":"Electrical Engineer","company":"YTL Power","location":"Kuala Lumpur","type":"Full-time","salary":"RM 4,500 – RM 8,000","posted":"4 days ago","url":"https://ricebowl.my","description":"Design and maintain electrical systems for power generation facilities. AutoCAD, IEC standards, and switchgear experience required.","skills":["Electrical Design","AutoCAD","IEC Standards","Switchgear","Power Systems","SCADA","PLC","Maintenance"]},
        {"id":"rb10","platform":"RiceBowl","title":"Sales Executive","company":"Digi Telecommunications","location":"Kuala Lumpur","type":"Full-time","salary":"RM 3,000 – RM 5,000 + Commission","posted":"1 day ago","url":"https://ricebowl.my","description":"Drive B2B sales of enterprise telecom solutions. Manage client relationships, prepare proposals, and hit monthly revenue targets.","skills":["Sales","B2B","Negotiation","CRM","Presentation","Communication","Networking","Target-driven"]},
        {"id":"rb11","platform":"RiceBowl","title":"Civil Engineer","company":"IJM Corporation","location":"Shah Alam","type":"Full-time","salary":"RM 4,000 – RM 7,000","posted":"5 days ago","url":"https://ricebowl.my","description":"Plan and supervise construction of roads, bridges, and infrastructure projects. AutoCAD, site supervision, and BIM experience preferred.","skills":["AutoCAD","Civil Engineering","Site Supervision","BIM","Structural Analysis","MS Project","Construction","Surveying"]},
        {"id":"rb12","platform":"RiceBowl","title":"Teacher (Secondary School — Science)","company":"Tenby International School","location":"Penang","type":"Full-time","salary":"RM 3,500 – RM 5,500","posted":"2 days ago","url":"https://ricebowl.my","description":"Teach Science and Biology to secondary school students. Develop lesson plans, assess student performance, and collaborate with parents. Teaching qualification required.","skills":["Teaching","Lesson Planning","Curriculum Development","Classroom Management","Assessment","Science","Biology","Communication"]},
    ],
    "linkedin": [
        {"id":"li1","platform":"LinkedIn","title":"Software Engineer (Full Stack)","company":"Accenture Malaysia","location":"Kuala Lumpur","type":"Full-time","salary":"RM 6,000 – RM 10,000","posted":"Today","url":"https://linkedin.com/jobs","description":"Develop enterprise web applications for banking and insurance clients. React, Node.js, and cloud deployment experience required.","skills":["React","Node.js","TypeScript","AWS","Docker","REST APIs","Agile","Git"]},
        {"id":"li2","platform":"LinkedIn","title":"Data Engineer","company":"Petronas Digital","location":"Kuala Lumpur","type":"Full-time","salary":"RM 7,000 – RM 12,000","posted":"1 day ago","url":"https://linkedin.com/jobs","description":"Build and maintain scalable data pipelines using Spark, Airflow, and BigQuery. Strong Python and SQL skills required.","skills":["Python","Apache Spark","Airflow","BigQuery","SQL","ETL","Kafka","Data Pipelines"]},
        {"id":"li3","platform":"LinkedIn","title":"Brand Manager","company":"Unilever Malaysia","location":"Petaling Jaya","type":"Full-time","salary":"RM 6,000 – RM 10,000","posted":"2 days ago","url":"https://linkedin.com/jobs","description":"Lead brand strategy and marketing campaigns for FMCG products. Experience with consumer insights, campaign planning, and agency management required.","skills":["Brand Management","Marketing Strategy","Campaign Planning","Consumer Insights","Analytics","Budget Management","Communication","Leadership"]},
        {"id":"li4","platform":"LinkedIn","title":"Machine Learning Engineer","company":"Fusionex","location":"Kuala Lumpur","type":"Full-time","salary":"RM 8,000 – RM 15,000","posted":"3 days ago","url":"https://linkedin.com/jobs","description":"Build and deploy ML models for computer vision and NLP tasks. PyTorch, MLflow, and cloud deployment required. Experience with LLMs is a plus.","skills":["Python","PyTorch","Machine Learning","NLP","Computer Vision","MLflow","AWS","Deep Learning"]},
        {"id":"li5","platform":"LinkedIn","title":"Finance Manager","company":"Top Glove","location":"Shah Alam","type":"Full-time","salary":"RM 8,000 – RM 14,000","posted":"4 days ago","url":"https://linkedin.com/jobs","description":"Oversee financial planning, budgeting, and reporting for manufacturing operations. CPA/ACCA required, SAP experience strongly preferred.","skills":["Financial Planning","Budgeting","SAP","Excel","Financial Reporting","ACCA","Auditing","Leadership"]},
        {"id":"li6","platform":"LinkedIn","title":"iOS Developer","company":"Boost","location":"Kuala Lumpur","type":"Full-time","salary":"RM 6,000 – RM 10,000","posted":"1 day ago","url":"https://linkedin.com/jobs","description":"Build and maintain iOS features for Malaysia's leading e-wallet app. Swift, SwiftUI, and experience with fintech or payments is a plus.","skills":["Swift","SwiftUI","iOS","Xcode","REST APIs","Git","Agile","Firebase"]},
        {"id":"li7","platform":"LinkedIn","title":"UX Researcher","company":"Carsome","location":"Kuala Lumpur","type":"Full-time","salary":"RM 5,000 – RM 8,000","posted":"2 days ago","url":"https://linkedin.com/jobs","description":"Plan and conduct user research studies, usability tests, and interviews. Synthesise insights to inform product decisions.","skills":["UX Research","Usability Testing","User Interviews","Figma","Data Analysis","Survey Design","Personas","Communication"]},
        {"id":"li8","platform":"LinkedIn","title":"Quantity Surveyor","company":"Gamuda","location":"Shah Alam","type":"Full-time","salary":"RM 4,000 – RM 7,000","posted":"3 days ago","url":"https://linkedin.com/jobs","description":"Manage cost estimation, bills of quantities, and contract administration for infrastructure projects. AutoCAD and MS Project experience required.","skills":["Quantity Surveying","Cost Estimation","Bills of Quantities","AutoCAD","MS Project","Contract Management","Construction","RICS"]},
        {"id":"li9","platform":"LinkedIn","title":"Nurse (Registered)","company":"Gleneagles Hospital","location":"Kuala Lumpur","type":"Full-time","salary":"RM 3,500 – RM 5,500","posted":"Today","url":"https://linkedin.com/jobs","description":"Provide patient care in a busy surgical ward. Valid Malaysian nursing licence required. ICU or surgical ward experience preferred.","skills":["Patient Care","Clinical Assessment","Medication Administration","Wound Care","ICU","Documentation","BLS","Communication"]},
        {"id":"li10","platform":"LinkedIn","title":"Operations Manager","company":"DHL Malaysia","location":"Shah Alam","type":"Full-time","salary":"RM 7,000 – RM 12,000","posted":"4 days ago","url":"https://linkedin.com/jobs","description":"Oversee logistics operations, warehouse management, and last-mile delivery efficiency. Experience with WMS and fleet management required.","skills":["Operations Management","Logistics","Warehouse Management","WMS","KPI Tracking","Team Leadership","Supply Chain","Process Improvement"]},
    ],
    "indeed": [
        {"id":"in1","platform":"Indeed","title":"Junior Software Developer","company":"Revenue Monster","location":"Kuala Lumpur","type":"Full-time","salary":"RM 3,500 – RM 5,500","posted":"Today","url":"https://indeed.com/jobs","description":"Build REST APIs and web features using PHP Laravel and Vue.js. Fresh graduates are welcome. Mentorship provided.","skills":["PHP","Laravel","Vue.js","MySQL","REST APIs","Git","HTML","CSS"]},
        {"id":"in2","platform":"Indeed","title":"Data Entry & Analytics Clerk","company":"Parkson","location":"Kuala Lumpur","type":"Full-time","salary":"RM 2,500 – RM 3,500","posted":"1 day ago","url":"https://indeed.com/jobs","description":"Manage data entry, generate reports, and support the analytics team. Excel and basic SQL knowledge required.","skills":["Excel","Data Entry","SQL","Reporting","Microsoft Office","Attention to Detail","Communication","Data Validation"]},
        {"id":"in3","platform":"Indeed","title":"Social Media Executive","company":"FashionValet","location":"Kuala Lumpur","type":"Full-time","salary":"RM 3,000 – RM 4,500","posted":"2 days ago","url":"https://indeed.com/jobs","description":"Manage social media accounts, create content, run paid campaigns, and grow community engagement across Instagram, TikTok, and Facebook.","skills":["Social Media","Content Creation","Instagram","TikTok","Copywriting","Photography","Canva","Analytics"]},
        {"id":"in4","platform":"Indeed","title":"Embedded Systems Engineer","company":"Keysight Technologies","location":"Penang","type":"Full-time","salary":"RM 5,000 – RM 9,000","posted":"3 days ago","url":"https://indeed.com/jobs","description":"Develop firmware for electronic test equipment using C and C++. Experience with RTOS, hardware debugging, and low-level programming required.","skills":["C","C++","Embedded Systems","RTOS","Firmware","Hardware Debugging","Python","Electronics"]},
        {"id":"in5","platform":"Indeed","title":"Pharmacy Assistant","company":"Guardian Health & Beauty","location":"Multiple Locations","type":"Full-time","salary":"RM 2,500 – RM 3,500","posted":"4 days ago","url":"https://indeed.com/jobs","description":"Assist pharmacists, manage inventory, and advise customers on over-the-counter medications. Diploma in Pharmacy required.","skills":["Pharmacy","Medication Dispensing","Customer Service","Inventory Management","Health Advice","Communication","Compliance","Record Keeping"]},
        {"id":"in6","platform":"Indeed","title":"Lecturer (Computer Science)","company":"Multimedia University","location":"Cyberjaya","type":"Full-time","salary":"RM 5,000 – RM 9,000","posted":"1 day ago","url":"https://indeed.com/jobs","description":"Teach undergraduate modules in programming, data structures, and algorithms. Master's degree in CS or related field required. Research experience is a plus.","skills":["Teaching","Curriculum Development","Python","Java","Data Structures","Algorithms","Research","Academic Writing"]},
        {"id":"in7","platform":"Indeed","title":"Supply Chain Analyst","company":"Nestlé Malaysia","location":"Petaling Jaya","type":"Full-time","salary":"RM 4,500 – RM 7,500","posted":"2 days ago","url":"https://indeed.com/jobs","description":"Analyse supply chain performance, manage vendor data, and optimise inventory levels. SAP and Excel expertise required.","skills":["Supply Chain","SAP","Excel","Inventory Management","Data Analysis","Vendor Management","Forecasting","Logistics"]},
        {"id":"in8","platform":"Indeed","title":"Psychologist / Counsellor","company":"Mind & Soul Clinic","location":"Kuala Lumpur","type":"Full-time","salary":"RM 4,000 – RM 6,500","posted":"3 days ago","url":"https://indeed.com/jobs","description":"Provide individual and group counselling sessions. Conduct psychological assessments and develop treatment plans. Registered with Malaysian Board of Counsellors required.","skills":["Counselling","Psychological Assessment","CBT","Mental Health","Report Writing","Empathy","Communication","Ethics"]},
        {"id":"in9","platform":"Indeed","title":"Chef de Partie","company":"Mandarin Oriental KL","location":"Kuala Lumpur","type":"Full-time","salary":"RM 3,500 – RM 5,500","posted":"Today","url":"https://indeed.com/jobs","description":"Lead a section of the kitchen in a 5-star hotel. Experience in Western or Asian fine dining required. Culinary qualification preferred.","skills":["Cooking","Menu Development","Food Safety","Kitchen Management","HACCP","Team Leadership","Inventory","Plating"]},
        {"id":"in10","platform":"Indeed","title":"Legal Associate","company":"Skrine & Co","location":"Kuala Lumpur","type":"Full-time","salary":"RM 4,500 – RM 7,500","posted":"4 days ago","url":"https://indeed.com/jobs","description":"Handle corporate and commercial matters including M&A, contracts, and due diligence. LLB required and called to the Malaysian Bar.","skills":["Corporate Law","Contract Drafting","Due Diligence","Legal Research","M&A","Negotiation","Communication","Compliance"]},
    ],
    "glassdoor": [
        {"id":"gd1","platform":"Glassdoor","title":"Site Reliability Engineer","company":"Sea Group","location":"Kuala Lumpur","type":"Full-time","salary":"RM 9,000 – RM 16,000","posted":"Today","url":"https://glassdoor.com/jobs","description":"Ensure reliability, scalability, and performance of production systems. Python, Kubernetes, and observability tooling (Prometheus, Grafana) required.","skills":["Python","Kubernetes","Docker","Prometheus","Grafana","Linux","CI/CD","AWS"]},
        {"id":"gd2","platform":"Glassdoor","title":"Chartered Accountant (ACCA)","company":"KPMG Malaysia","location":"Kuala Lumpur","type":"Full-time","salary":"RM 5,500 – RM 9,000","posted":"1 day ago","url":"https://glassdoor.com/jobs","description":"Perform audit and assurance engagements for large corporate clients. ACCA qualification required. Experience with IFRS and financial instruments preferred.","skills":["Auditing","ACCA","IFRS","Financial Analysis","Excel","SAP","Tax","Risk Assessment"]},
        {"id":"gd3","platform":"Glassdoor","title":"Marketing Manager","company":"Maxis","location":"Kuala Lumpur","type":"Full-time","salary":"RM 8,000 – RM 14,000","posted":"2 days ago","url":"https://glassdoor.com/jobs","description":"Lead integrated marketing campaigns for consumer and enterprise products. Team leadership, budget management, and digital marketing expertise required.","skills":["Marketing Strategy","Campaign Management","Digital Marketing","Budget Management","Leadership","Brand Management","Analytics","Communication"]},
        {"id":"gd4","platform":"Glassdoor","title":"Biomedical Engineer","company":"Siemens Healthineers","location":"Petaling Jaya","type":"Full-time","salary":"RM 5,000 – RM 9,000","posted":"3 days ago","url":"https://glassdoor.com/jobs","description":"Install, maintain, and troubleshoot medical imaging equipment. Degree in biomedical or electrical engineering required. Experience with MRI or CT machines preferred.","skills":["Biomedical Engineering","Medical Equipment","Troubleshooting","Electronics","Documentation","Customer Service","Calibration","Safety"]},
        {"id":"gd5","platform":"Glassdoor","title":"Project Manager (IT)","company":"IBM Malaysia","location":"Kuala Lumpur","type":"Full-time","salary":"RM 8,000 – RM 14,000","posted":"4 days ago","url":"https://glassdoor.com/jobs","description":"Lead IT project delivery for enterprise clients. PMP or PRINCE2 certification required. Agile and waterfall experience, strong stakeholder management skills.","skills":["Project Management","PMP","Agile","Waterfall","Stakeholder Management","Risk Management","JIRA","MS Project"]},
        {"id":"gd6","platform":"Glassdoor","title":"Environmental Consultant","company":"ERM Malaysia","location":"Kuala Lumpur","type":"Full-time","salary":"RM 4,500 – RM 8,000","posted":"1 day ago","url":"https://glassdoor.com/jobs","description":"Conduct environmental impact assessments, site audits, and sustainability reports for industrial clients. Degree in environmental science or engineering required.","skills":["Environmental Assessment","EIA","Sustainability","Report Writing","Field Work","ISO 14001","GIS","Communication"]},
        {"id":"gd7","platform":"Glassdoor","title":"Customer Success Manager","company":"Salesforce","location":"Kuala Lumpur","type":"Full-time","salary":"RM 7,000 – RM 12,000","posted":"2 days ago","url":"https://glassdoor.com/jobs","description":"Drive adoption and retention for Salesforce enterprise customers. Build relationships, run business reviews, and identify expansion opportunities.","skills":["Customer Success","CRM","Salesforce","Account Management","Communication","Analytics","Presentation","Upselling"]},
        {"id":"gd8","platform":"Glassdoor","title":"Sports Science Officer","company":"National Sports Institute","location":"Bukit Jalil","type":"Full-time","salary":"RM 3,500 – RM 5,500","posted":"3 days ago","url":"https://glassdoor.com/jobs","description":"Support national athletes with performance analysis, fitness testing, and injury prevention. Degree in sports science or physiology required.","skills":["Sports Science","Performance Analysis","Fitness Testing","Nutrition","Physiology","Data Analysis","Communication","Coaching"]},
    ],
}


# ── JSON helpers ──────────────────────────────────────────────────────────────

def try_parse_json(text: str):
    text = text.strip()
    if not text:
        return None
    try:
        r = json.loads(text)
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    try:
        r = json.loads(text.replace("'", '"'))
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return None


def extract_json_from_response(raw: str):
    if not raw:
        return None
    # Strip reasoning blocks (e.g. <think>...</think>)
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()

    # Direct parse
    r = try_parse_json(cleaned)
    if r:
        return r

    # Fenced code blocks
    for pat in [r"```json\s*([\s\S]*?)```", r"```\s*([\s\S]*?)```"]:
        m = re.search(pat, cleaned, re.IGNORECASE)
        if m:
            r = try_parse_json(m.group(1))
            if r:
                return r

    # Brace-depth scan (outermost {})
    first = cleaned.find("{")
    if first != -1:
        depth = 0
        for i, ch in enumerate(cleaned[first:], first):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    r = try_parse_json(cleaned[first:i+1])
                    if r:
                        return r
                    break

    return None


# ── Skill-based score calculator (used as fallback if LLM JSON parse fails) ──

def compute_score_from_skills(profile: dict, job: dict) -> dict:
    """
    Deterministic fallback scoring based on actual skill overlap.
    This ensures we NEVER return a flat 50/50/50 score.
    """
    cand_skills = set(s.lower() for s in profile.get("skills", []))
    job_skills  = set(s.lower() for s in job.get("skills", []))

    # Skills score: Jaccard-style overlap
    if job_skills:
        matched = cand_skills & job_skills
        skills_score = round(len(matched) / len(job_skills) * 100)
    else:
        matched = set()
        skills_score = 0

    # Experience score: compare candidate years to a rough job-level estimate
    cand_exp = int(profile.get("experience_years", 0) or 0)
    job_title_lower = job.get("title", "").lower()
    job_desc_lower  = job.get("description", "").lower()
    if any(w in job_title_lower for w in ["senior", "lead", "principal", "manager", "head"]):
        required_exp = 5
    elif any(w in job_title_lower for w in ["junior", "fresh", "graduate", "intern", "assistant"]):
        required_exp = 0
    elif any(w in job_desc_lower for w in ["3 years", "3+ years", "4 years", "5 years"]):
        required_exp = 3
    else:
        required_exp = 2
    if cand_exp >= required_exp + 2:
        experience_score = 90
    elif cand_exp >= required_exp:
        experience_score = 75
    elif cand_exp >= required_exp - 1:
        experience_score = 55
    elif cand_exp == 0 and required_exp == 0:
        experience_score = 70
    else:
        experience_score = max(10, 40 - (required_exp - cand_exp) * 10)

    # Education score: keyword presence in job description
    cand_edu = (profile.get("education", "") or "").lower()
    if any(w in cand_edu for w in ["phd", "doctor"]):
        education_score = 95
    elif any(w in cand_edu for w in ["master", "msc", "mba"]):
        education_score = 85
    elif any(w in cand_edu for w in ["degree", "bachelor", "bsc", "beng", "ba "]):
        education_score = 75
    elif any(w in cand_edu for w in ["diploma", "cert"]):
        education_score = 55
    else:
        education_score = 40

    # Overall: weighted (skills 50%, experience 30%, education 20%)
    overall = round(skills_score * 0.50 + experience_score * 0.30 + education_score * 0.20)

    # Verdict
    if overall >= 75:
        verdict = "Strong Match"
    elif overall >= 55:
        verdict = "Good Match"
    elif overall >= 35:
        verdict = "Partial Match"
    else:
        verdict = "Weak Match"

    matched_display = [s for s in job.get("skills", []) if s.lower() in cand_skills]
    missing_display = [s for s in job.get("skills", []) if s.lower() not in cand_skills]

    return {
        "overall_score":    overall,
        "skills_score":     skills_score,
        "experience_score": experience_score,
        "education_score":  education_score,
        "matched_skills":   matched_display,
        "missing_skills":   missing_display,
        "verdict":          verdict,
        "one_liner":        f"Based on skill overlap and experience — {len(matched_display)} of {len(job.get('skills',[]))} required skills matched.",
    }


# ── LLM call ──────────────────────────────────────────────────────────────────

def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MORPHEUS_API_KEY}",
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]
    last_error = None
    for model in MORPHEUS_MODELS:
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.1}
        try:
            r = requests.post(MORPHEUS_URL, headers=headers, json=payload, timeout=90)
            if r.status_code == 404:
                last_error = f"Model '{model}' not found"
                print(f"[Morpheus] {last_error} — trying next...")
                continue
            if r.status_code in (401, 403):
                raise Exception(f"Invalid API key (HTTP {r.status_code})")
            if not r.ok:
                last_error = f"HTTP {r.status_code}: {r.text[:300]}"
                print(f"[Morpheus] {model}: {last_error} — trying next...")
                continue
            content = r.json()["choices"][0]["message"]["content"].strip()
            print(f"[Morpheus] OK with '{model}'\n--- RAW ---\n{content[:600]}\n---")
            return content
        except Exception as e:
            if "Invalid API key" in str(e):
                raise
            last_error = str(e)
            print(f"[Morpheus] {model}: {last_error}")
            continue
    raise Exception(f"All models failed. Last error: {last_error}")


# ── File helpers ──────────────────────────────────────────────────────────────

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    if ext == "txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == "pdf":
        if not PDF_OK:
            raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")
        text = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
        return "\n".join(text)
    if ext == "docx":
        if not DOCX_OK:
            raise RuntimeError("python-docx not installed. Run: pip install python-docx")
        doc = DocxDocument(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f"Unsupported file type: {ext}")


def _extract_skills(text):
    keywords = [
        "Python","Java","JavaScript","TypeScript","React","Node.js","Go","Rust","C++","C#","PHP",
        "SQL","PostgreSQL","MySQL","MongoDB","Redis","AWS","Azure","GCP","Docker","Kubernetes",
        "Terraform","CI/CD","Git","Linux","REST","GraphQL","Machine Learning","Deep Learning",
        "TensorFlow","PyTorch","Figma","Photoshop","Illustrator","Excel","Power BI","Tableau",
        "Product Management","Agile","Scrum","SEO","Google Ads","Marketing","Cybersecurity",
        "AutoCAD","SolidWorks","MATLAB","Accounting","SAP","Auditing","Teaching","Nursing",
        "Counselling","Swift","Kotlin","Android","iOS","Networking","Cisco","Firewall",
    ]
    return [k for k in keywords if re.search(rf"\b{re.escape(k)}\b", text, re.IGNORECASE)][:12]


def sanitise_profile(p: dict) -> dict:
    p.setdefault("name", "Not found")
    p.setdefault("major", "Professional")
    p.setdefault("level", "Mid-level")
    p.setdefault("summary", "")
    p.setdefault("skills", [])
    p.setdefault("education", "Not specified")
    p.setdefault("experience_years", 0)
    p.setdefault("search_keywords", [p.get("major", "")])
    for k in ("skills", "search_keywords"):
        if isinstance(p[k], str):
            p[k] = [s.strip() for s in re.split(r"[,;]", p[k]) if s.strip()]
    try:
        p["experience_years"] = int(float(str(p["experience_years"])))
    except Exception:
        p["experience_years"] = 0
    return p


def sanitise_score(d: dict) -> dict:
    for k in ("overall_score","skills_score","experience_score","education_score"):
        try:
            d[k] = max(0, min(100, int(float(str(d[k])))))
        except Exception:
            d[k] = 0
    d.setdefault("matched_skills", [])
    d.setdefault("missing_skills", [])
    d.setdefault("verdict", "Partial Match")
    d.setdefault("one_liner", "")
    return d


def extract_profile_from_text(raw: str, resume_text: str = "") -> dict:
    profile = {
        "name": "Not found", "major": "Professional", "level": "Mid-level",
        "summary": "", "skills": [], "education": "Not specified",
        "experience_years": 0, "search_keywords": [],
    }
    for line in raw.splitlines():
        line = line.strip().strip(",").strip('"').strip("'")
        for key in profile:
            m = re.match(rf'["\']?{key}["\']?\s*[:=]\s*["\']?(.+?)["\']?\s*$', line, re.IGNORECASE)
            if m:
                val = m.group(1).strip().strip('"').strip("'").strip(",")
                if key in ("skills", "search_keywords"):
                    items = [s.strip().strip('"').strip("'") for s in re.split(r"[,\[\]]", val) if s.strip()]
                    if items:
                        profile[key] = items
                elif key == "experience_years":
                    try:
                        profile[key] = int(float(re.sub(r"[^\d.]", "", val) or "0"))
                    except Exception:
                        pass
                else:
                    if val and val.lower() not in ("null","none",""):
                        profile[key] = val
    if not profile["skills"] and resume_text:
        profile["skills"] = _extract_skills(resume_text)
    if not profile["search_keywords"]:
        profile["search_keywords"] = [profile["major"]]
    return profile


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/debug-llm", methods=["GET"])
def debug_llm():
    system = "You output only valid JSON. No markdown. No explanation."
    user   = 'Return exactly this JSON: {"status": "ok", "model": "working"}'
    try:
        raw    = call_llm(system, user, max_tokens=100)
        parsed = extract_json_from_response(raw)
        return jsonify({"raw_response": raw, "parsed_ok": parsed is not None, "parsed": parsed})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/parse-resume", methods=["POST"])
def parse_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["resume"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    try:
        raw_text = extract_text_from_file(filepath)
    except Exception as e:
        return jsonify({"error": f"Could not read file: {str(e)}"}), 500
    finally:
        try: os.remove(filepath)
        except: pass

    if len(raw_text.strip()) < 50:
        return jsonify({"error": "Could not extract enough text. Try a different format."}), 400

    system = (
        "You are a resume parser API. "
        "You respond with ONLY a raw JSON object — nothing else. "
        "No markdown. No code fences. No explanation. "
        "The very first character of your response must be { and the last must be }."
    )
    user = (
        "Parse the resume below. Respond with a single JSON object with these exact keys: "
        "name, major, level, summary, skills, education, experience_years, search_keywords.\n\n"
        "Rules:\n"
        "- level: one of Fresher / Junior / Mid-level / Senior / Lead\n"
        "- skills: JSON array of strings (list ALL technical and professional skills found)\n"
        "- search_keywords: JSON array of 3 job title strings to search for\n"
        "- experience_years: integer\n\n"
        f"Resume:\n{raw_text[:3000]}"
    )

    try:
        raw = call_llm(system, user, max_tokens=800)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    profile = extract_json_from_response(raw)
    if profile is None:
        print(f"[parse-resume] JSON parse failed — using text fallback")
        profile = extract_profile_from_text(raw, raw_text)

    profile = sanitise_profile(profile)
    return jsonify({"profile": profile, "engine": "Morpheus AI (mor.org)"})


@app.route("/api/jobs", methods=["POST"])
def get_jobs():
    data      = request.json
    platforms = data.get("platforms", ["jobstreet", "ricebowl"])
    query     = data.get("query", "")

    results = {}
    q_words = [w for w in query.lower().split() if len(w) > 2]

    for p in platforms:
        if p not in MOCK_JOBS:
            continue
        if not q_words:
            results[p] = MOCK_JOBS[p]
            continue
        scored = sorted(
            MOCK_JOBS[p],
            key=lambda job: -sum(
                1 for w in q_words
                if w in job["title"].lower()
                or any(w in s.lower() for s in job["skills"])
                or w in job["description"].lower()
            )
        )
        results[p] = scored

    return jsonify(results)


@app.route("/api/match", methods=["POST"])
def match_job():
    data    = request.json
    profile = data.get("profile", {})
    job     = data.get("job", {})
    mode    = data.get("mode", "score")

    if not profile or not job:
        return jsonify({"error": "Profile and job data are required"}), 400

    candidate = (
        f"Name: {profile.get('name','Unknown')}\n"
        f"Profession: {profile.get('major','')} ({profile.get('level','')})\n"
        f"Experience: {profile.get('experience_years',0)} years\n"
        f"Skills: {', '.join(profile.get('skills',[]))}\n"
        f"Education: {profile.get('education','')}\n"
        f"Summary: {profile.get('summary','')}"
    )
    job_info = (
        f"Job Title: {job.get('title','')}\n"
        f"Company: {job.get('company','')}\n"
        f"Description: {job.get('description','')}\n"
        f"Required Skills: {', '.join(job.get('skills',[]))}"
    )

    if mode == "score":
        system = (
            "You are a strict recruiter scoring a job match. "
            "Respond with ONLY a raw JSON object. "
            "First character must be { and last must be }. No markdown. No explanation."
        )
        user = (
            "Score how well this CANDIDATE matches this JOB. "
            "Be accurate — if the candidate's skills and profession do not match the job requirements, "
            "give a LOW score (below 40). If they are a strong match, give a HIGH score (above 75). "
            "Do NOT default to 50. Base your scores on actual skill overlap and relevance.\n\n"
            "Return a JSON object with EXACTLY these keys:\n"
            "- overall_score: integer 0-100\n"
            "- skills_score: integer 0-100\n"
            "- experience_score: integer 0-100\n"
            "- education_score: integer 0-100\n"
            "- matched_skills: array of skill strings found in BOTH candidate and job\n"
            "- missing_skills: array of job-required skills the candidate lacks\n"
            "- verdict: exactly one of: Strong Match / Good Match / Partial Match / Weak Match\n"
            "- one_liner: one honest sentence summarising the match\n\n"
            f"CANDIDATE:\n{candidate}\n\nJOB:\n{job_info}"
        )
        try:
            raw    = call_llm(system, user, max_tokens=500)
            result = extract_json_from_response(raw)

            if result is None:
                # ── REAL fallback: compute actual skill-overlap score, NOT flat 50 ──
                print("[match] LLM JSON parse failed — using skill-overlap fallback scorer")
                result = compute_score_from_skills(profile, job)
            else:
                # Validate the LLM didn't return uniform 50s
                scores = [result.get("overall_score"), result.get("skills_score"),
                          result.get("experience_score"), result.get("education_score")]
                if all(s == 50 for s in scores if s is not None):
                    print("[match] LLM returned uniform 50s — replacing with skill-overlap scorer")
                    result = compute_score_from_skills(profile, job)

            return jsonify({"mode": "score", "data": sanitise_score(result), "engine": "Morpheus AI (mor.org)"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:  # full report
        system = "You are a career coach. Write a detailed, honest, and specific match report."
        user = (
            "Write a structured match report. Be specific and honest — if the candidate's background "
            "does not match the job, say so clearly and constructively.\n\n"
            "Sections:\n"
            "1. Match Overview\n2. Strengths\n3. Skill Gaps\n"
            "4. Experience Analysis\n5. Recommendations (3 actions)\n"
            "6. Interview Tips (2-3 questions)\n\n"
            f"CANDIDATE:\n{candidate}\n\nJOB:\n{job_info}"
        )
        try:
            result = call_llm(system, user, max_tokens=1200)
            return jsonify({"mode": "report", "data": result, "engine": "Morpheus AI (mor.org)"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 52)
    print("  ResuMatch — AI-Powered Job Matching System")
    print("  Powered by Morpheus AI (mor.org)")
    print("  http://127.0.0.1:5000")
    print("  Debug: http://127.0.0.1:5000/api/debug-llm")
    print("=" * 52)
    missing = []
    if not PDF_OK:  missing.append("pdfplumber")
    if not DOCX_OK: missing.append("python-docx")
    if missing:
        print(f"\n  [!] Missing: {', '.join(missing)}")
        print(f"      pip install {' '.join(missing)}\n")
    app.run(debug=True, port=5000)