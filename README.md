# StartSmart UAE — Test Your Idea Before You Spend

> **Tatweer Hackathon 2026 · Challenge 1: Taking the first entrepreneurial step**
> A bilingual (Arabic/English) AI assistant that turns a business idea into a first action, validation plan, opportunity score, 10-person proof test, founder decision, and a professional PDF report — built for first-time founders in Al Qua'a and rural Al Ain.

**Live demo:** _[paste your Render URL]_
**Demo video (2 min):** _[paste your YouTube link]_

---

## Challenge selected

Challenge 1 — Taking the first entrepreneurial step.

## Problem

Many first-time founders in rural communities like Al Qua'a have an idea or a skill but do not know the first practical step, what to test, or how to avoid spending money too early. There is no advisor nearby, and generic online advice is written for Dubai free zones, not a camel-farming, stargazing-tourism community.

## Target users

Al Qua'a residents, students, camel-farm families, local farmers, farm workers, small traders, and tourism-related entrepreneurs — including people who think and read in Arabic.

## Solution

StartSmart UAE turns a business idea into a first action, a 7-day validation plan, five customer questions, a WhatsApp test message, an opportunity score, a 10-person proof-mode feedback summary, a clear founder decision, and a downloadable founder report — all in under five minutes, in English or Arabic.

## Main features

First Step Today · Opportunity Score /25 with reasons and improvement tips · Founder Decision Engine · Proof Mode (test with 10 people, with demo-fill and CSV export) · First 7 Days plan (action, output, time, success check) · Validation questions · WhatsApp test message (copy + open) · "What not to do yet" guidance · Founder Readiness Report · Shareable founder summary · Fuller path with cost/timeline charts · Suggested UAE resources · Follow-up AI chat · Arabic option with full RTL · Professional 5-page PDF report.



## Creative features (v6)

Beyond the core flow, StartSmart UAE includes judge-facing features that make the value obvious:

- **Founder Passport** — a startup-ID-style summary card (idea, status, first action, score, decision, channel, test cost, next step) with copy and PDF export.
- **Before You Spend** — shows money protected by testing first (planned budget − recommended first test), a clear impact visual.
- **Customer Personas** — three local personas (who they are, what they care about, how to reach them, what to ask).
- **Risk Radar** — five risks (demand, cost, trust, legal, execution) each with level, reason, and fix; legal stays guidance-only.
- **Pitch Generator** — 10-second, 30-second, WhatsApp, and Instagram pitches, each copyable.
- **Local Opportunity Map** — a clean Al Qua'a opportunity flow.
- **Validation QR Code** — customers scan to open the WhatsApp test message.
- **Judge Mode** — guides judges through the strongest sections with highlights.
- **Animated Proof Mode** — demo feedback fills customer-by-customer for a strong live demo.
- **Floating Founder Advisor** — fixed chat with a local fallback so it never shows rate-limit errors.

All of these appear in the PDF report where relevant, work in Arabic, and respect reduced-motion.

## How StartSmart UAE meets the judging criteria

| Criterion | How the project meets it |
|---|---|
| Impact | Helps first-time founders take action and avoid wasting money |
| Relevance | Directly solves Challenge 1, built for the Al Qua'a / Al Ain context |
| Feasibility | Simple Flask web app, free API tier, no database, no complex setup |
| Readiness | Working prototype: plan, score, Proof Mode, decision, PDF, follow-ups |
| Scalability | Adapts to other UAE rural communities by changing examples and resources |
| Evidence | Proof Mode collects interest, price, concerns, and pre-order intent; CSV export |
| Documentation | README, TESTING.md, demo script, screenshots, run instructions |

## Testable claims

- A user can generate a first-step action plan in under 5 minutes.
- The app produces 5 validation questions for every idea.
- The app gives an opportunity score out of 25 with a reason and improvement tip per category.
- Proof Mode summarises feedback from up to 10 customers into a live verdict.
- The app helps founders test demand before spending the full budget.
- The app can be adapted to other rural communities by changing examples and resources.

## Feasibility

Runs on the free Groq API tier (Llama 3.1) — effectively zero cost at community scale. Single Flask app, deployable free on Render. No database, no auth. The only component needing occasional updating is the system prompt, as rules change. Mobile-first and works on a phone over a basic connection.

## Scalability

Change the location and examples in one prompt to serve any UAE emirate or rural community. The bilingual pattern extends to other languages. The same idea-to-validation engine generalises to any first-step guidance problem.

## Tools used

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| AI | Groq API · Llama 3.1 (free tier) |
| Charts | Chart.js (web) + matplotlib (PDF) |
| PDF | ReportLab (server-side, with Arabic via Amiri font + reshaping) |
| Languages | English + Arabic (native RTL) |
| Hosting | Render.com (free) |

## How to run

```bash
git clone https://github.com/RVS0MRk/startsmart-uae
cd startsmart-uae
python -m venv .venv
.venv\Scripts\activate          # Windows  (use: source .venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
```

Add your free Groq key (from console.groq.com) as a file named `secret.txt` in the project root, OR as an environment variable `GROQ_API_KEY`. Then:

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

> Note: the first Arabic PDF download fetches the Amiri Arabic font once (needs internet); after that it works offline.

## Screenshots

_Add screenshots of: home/input, generated plan with judge summary, opportunity score, Proof Mode with demo feedback, the founder decision card, the PDF report, and one Arabic screen._

## Demo video

See `DEMO_SCRIPT.md` for the 2-minute script. _[paste your YouTube link]_

---

## Team

Built for the Tatweer Hackathon 2026, in collaboration with Abu Dhabi University.

- _[Your name]_
- _[Teammate name]_

_StartSmart UAE — because the hardest part of starting is knowing where to start._
