"""
Dataset Generator — LinkedIn SpamGuard AI
Generates a synthetic labeled dataset of job posts for training.
Labels: 0 = FAKE, 1 = SUSPICIOUS, 2 = LEGIT
"""

import csv
import os
import random

random.seed(42)

# ── Templates ────────────────────────────────────────────────────────────────

FAKE_TEMPLATES = [
    "URGENT HIRING!! Earn ${salary}/week working from home. No experience needed. Apply NOW on WhatsApp: +91{phone}. Limited slots!",
    "A leading company is looking for candidates. NO DEGREE REQUIRED. Earn upto ${salary} daily! Contact us on Gmail: recruit{num}@gmail.com",
    "Work from home and earn {salary}k monthly! Any qualification accepted. Hurry, deadline soon. Apply here: bit.ly/job{num}",
    "EASY JOB!!! Earn ${salary} per day. Just {task} from home. No experience necessary! WhatsApp {phone} to apply FAST.",
    "Guaranteed income of ${salary} weekly. Part time job, full time pay. Our organization is hiring urgently. Don't miss this opportunity! Apply: forms.gle/job{num}",
    "Confidential company hiring freshers. Earn unlimited income! No interview. Direct joining. WhatsApp +91{phone}. Apply immediately!",
    "HIGH PAY job offer!! ${salary}/week guaranteed. Work from home. No qualification needed. Contact: jobs{num}@yahoo.com Limited openings!!!",
    "URGENT: Data entry work from home. Earn Rs.{salary}/day. Send your resume to quickhire{num}@gmail.com. Act now!",
    "WE ARE HIRING!!! Earn ${salary} daily. Passive income guaranteed. No skills required. Apply before slots fill. Telegram: t.me/hire{num}",
    "Part time opportunity!! Earn {salary}k per week. A reputed company is expanding. No experience required! Call +91{phone} NOW.",
    "Exciting job!! Earn big from home. Unlimited earning potential. Easy tasks. No experience needed. Contact: hire{num}@hotmail.com. Hurry!!!",
    "LAST CHANCE! Work from home, earn ${salary}/week. Zero investment. Guaranteed salary. Apply via bit.ly/apply{num}. WhatsApp: {phone}",
]

SUSPICIOUS_TEMPLATES = [
    "{company} is hiring for a {role} position. Salary: up to ${salary}/month (negotiable). Send your CV to {company_email}. Freshers welcome.",
    "A well-known company in {city} is looking for a {role}. No prior experience needed. Salary: {salary}k. DM for details.",
    "We are hiring {role}s urgently. Our client is a leading firm. Apply now — limited positions available. Mail: hr{num}@gmail.com",
    "{company} seeks a {role}. Attractive salary package. Work from home option available. Contact our HR at {phone} to know more.",
    "Hiring for {role} immediately! {company} (a reputed organization) offers {salary}k/month. No interviews, direct selection. Send CV fast.",
    "Looking for {role} — freshers only. Company name will be disclosed after applying. Salary: {salary}k. Send resume to hr{num}@gmail.com",
    "Opportunity at {company}! {role} needed urgently. Earn {salary}k monthly. Flexible hours. Register here: forms.gle/reg{num}",
    "WALK-IN INTERVIEW at {company} for {role}. Salary: {salary}k-{salary2}k. Experience: 0-2 years. Hurry — limited seats!",
    "{company} is expanding its team. Hiring {role}. CTC: {salary} LPA. Apply now via WhatsApp: +91{phone}",
    "We have an opening for {role} at our confidential client company. Immediate joiners preferred. Email: recruiter{num}@outlook.com",
]

LEGIT_TEMPLATES = [
    "{company} is looking for a {role} with {exp}+ years of experience. Skills: {skills}. CTC: {salary}-{salary2} LPA. Apply at {company_url}/careers",
    "Job Opening at {company}: {role} | {city} | {exp}-{exp2} years | Skills: {skills} | Apply: LinkedIn or {company_url}/jobs",
    "{company} ({industry}) is hiring a {role}. Responsibilities: {resp}. Qualifications: {qual}. Competitive compensation. Apply via our website.",
    "We're expanding at {company}! Seeking a talented {role}. Role involves {resp}. Strong {skills} skills required. {exp}+ yrs exp. Apply: {company_url}",
    "{company} (NASDAQ: {ticker}) is hiring {role}s in {city}. Requirements: {qual}. Benefits: health, 401k, remote-friendly. careers.{company}.com",
    "Opportunity: {role} at {company} | Location: {city} | Experience: {exp}-{exp2} yrs | Salary: ₹{salary}-{salary2} LPA | Skills: {skills}",
    "{company} invites applications for the post of {role}. Required: {qual}, {exp} years experience. Apply before {date} via {company_url}/careers.",
    "Join {company}'s engineering team as a {role}. You'll work on {resp}. We offer {salary}-{salary2} LPA + ESOPs. careers.{company}.com",
    "Full-time {role} role at {company} (Series B startup). Stack: {skills}. Competitive salary, equity, flexible PTO. apply@{company}.com",
    "Position: {role} | Company: {company} | Industry: {industry} | CTC: {salary} LPA | Apply via Naukri or LinkedIn",
]

# ── Fill-in data ─────────────────────────────────────────────────────────────

COMPANIES    = ["TechCorp", "Infosys", "Wipro", "Deloitte", "Accenture", "Google", "Microsoft", "Amazon", "Razorpay", "Zepto", "CRED", "Swiggy", "Meesho"]
ROLES        = ["Software Engineer", "Data Analyst", "Product Manager", "Backend Developer", "Frontend Developer", "ML Engineer", "DevOps Engineer", "Business Analyst", "HR Executive"]
CITIES       = ["Bangalore", "Mumbai", "Hyderabad", "Pune", "Chennai", "Delhi", "Noida", "Gurgaon"]
SKILLS       = ["Python, SQL, ML", "React, Node.js", "Java, Spring Boot", "AWS, Docker", "Excel, Power BI", "Python, TensorFlow", "Go, Kubernetes"]
INDUSTRIES   = ["FinTech", "EdTech", "HealthTech", "E-Commerce", "SaaS", "IT Services", "Banking"]
RESP_LIST    = ["building scalable APIs", "analyzing large datasets", "leading cross-functional teams", "designing ML pipelines", "developing React UIs"]
QUAL_LIST    = ["B.Tech/B.E. in CS or related", "MBA from premier institute", "B.Sc. in Statistics", "MCA or equivalent"]
TICKERS      = ["INFY", "WIT", "GOOGL", "MSFT", "AMZN"]
DATES        = ["April 10, 2026", "April 30, 2026", "May 15, 2026"]


def _r(lst): return random.choice(lst)
def _n(lo, hi): return random.randint(lo, hi)


def _fake():
    t = _r(FAKE_TEMPLATES)
    return t.format(
        salary=_n(3000, 10000), phone=_n(7000000000, 9999999999),
        num=_n(100, 999), task=_r(["typing", "copy-paste", "data entry", "clicking ads"]),
    )


def _suspicious():
    t = _r(SUSPICIOUS_TEMPLATES)
    sal = _n(30, 80)
    return t.format(
        company=_r(COMPANIES), role=_r(ROLES), city=_r(CITIES),
        salary=sal, salary2=sal + _n(10, 30),
        company_email=f"hr{_n(1,99)}@gmail.com",
        num=_n(100, 999), phone=_n(7000000000, 9999999999),
    )


def _legit():
    t = _r(LEGIT_TEMPLATES)
    sal = _n(8, 25)
    comp = _r(COMPANIES)
    return t.format(
        company=comp, role=_r(ROLES), city=_r(CITIES),
        skills=_r(SKILLS), industry=_r(INDUSTRIES),
        exp=_n(1, 4), exp2=_n(5, 8),
        salary=sal, salary2=sal + _n(5, 15),
        resp=_r(RESP_LIST), qual=_r(QUAL_LIST),
        ticker=_r(TICKERS), date=_r(DATES),
        company_url=f"https://www.{comp.lower()}.com",
    )


# ── Manual Real-World Samples ──────────────────────────────────────────────────

REAL_FAKE_SAMPLES = [
    "I am looking for 10 people who want to earn $500 per day. No skills required. Just drop a YES below and message me directly on WhatsApp at +19876543210! URGENT!",
    "Work from home data entry jobs! Earn 50,000 INR weekly!! 100% Genuine company. Last chance to apply. Click forms.gle/spammy to register now.",
    "URGENT hiring for undisclosed multinational company. No interview required. Send your details to my personal yahoo mail: recruit2026@yahoo.com.",
    "Easy money online!! Part time work, full time pay. Earn up to $2000 weekly GUARANTEED. Contact us immediately to secure your spot.",
    "No experience needed. No degree required. We will train you to earn six figures in 30 days! Direct message me with 'INTERESTED' to start.",
]

REAL_SUSPICIOUS_SAMPLES = [
    "Hiring freshers for a well-known IT client. Salary up to 25k. Send your resume to hr.solutions@gmail.com. Immediate joiners only.",
    "Looking for a software engineer. Name of the company will be revealed in the interview. Send DM for details.",
    "Data Analyst needed urgently. Salary is highly competitive. Mail your CV to recruiter45@gmail.com.",
    "We are expanding our team. Various roles available. Freshers can apply. Salary: Negotiable. WhatsApp your resume to +919000000000.",
    "Job opportunity for recent graduates! Great package. Work from home option. Send us an email to know more.",
]

REAL_LEGIT_SAMPLES = [
    "Google is hiring a Senior Machine Learning Engineer in Bangalore. 5+ years of Python experience required. Apply directly through careers.google.com.",
    "We are looking for a Frontend Developer with strong React skills to join our team at TechCorp. The salary range is 15-20 LPA. Apply via the link below.",
    "Microsoft invites applications for the Business Analyst role in Hyderabad. Requirements: MBA, 2+ years experience in Power BI. Check our careers page.",
    "Open position: Backend Engineer (Java, Spring Boot) at Infosys. Minimum 3 years of experience. Apply on our official portal.",
    "Amazon is expanding the AWS team! We need Cloud Architects with Docker and Kubernetes experience. Competitive compensation package. careers.amazon.com",
]


# ── Generate & save ───────────────────────────────────────────────────────────

def generate_dataset(n_each: int = 80, output_path: str = "data/sample_jobs.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rows = []

    # Add templates
    for _ in range(n_each - len(REAL_FAKE_SAMPLES)):
        rows.append({"text": _fake(),       "label": 0, "label_name": "FAKE"})
    for _ in range(n_each - len(REAL_SUSPICIOUS_SAMPLES)):
        rows.append({"text": _suspicious(), "label": 1, "label_name": "SUSPICIOUS"})
    for _ in range(n_each - len(REAL_LEGIT_SAMPLES)):
        rows.append({"text": _legit(),      "label": 2, "label_name": "LEGIT"})
        
    # Add manual real-world samples
    for text in REAL_FAKE_SAMPLES:
        rows.append({"text": text,          "label": 0, "label_name": "FAKE"})
    for text in REAL_SUSPICIOUS_SAMPLES:
        rows.append({"text": text,          "label": 1, "label_name": "SUSPICIOUS"})
    for text in REAL_LEGIT_SAMPLES:
        rows.append({"text": text,          "label": 2, "label_name": "LEGIT"})

    random.shuffle(rows)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "label_name"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Dataset saved → {output_path}  ({len(rows)} hybrid rows - synthetic + real-world)")
    return rows


if __name__ == "__main__":
    generate_dataset(n_each=80, output_path="data/sample_jobs.csv")
