from flask import Flask, render_template, request, jsonify, send_file
import requests, json, os, io, urllib.request

app = Flask(__name__)

API_KEY = os.environ.get("GROQ_API_KEY", "")
if not API_KEY and os.path.exists("secret.txt"):
    API_KEY = open("secret.txt").read().strip()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

SCHEMA = """{
  "business_name_suggestion": "string",
  "summary": "one-sentence description",
  "judge_summary": {"problem": "string", "target_user": "string", "solution": "string", "impact": "string", "evidence": "string", "why_local": "string"},
  "first_step_today": "ONE specific customer-facing action doable TODAY in under 2 hours, no license/setup, tests demand. e.g. 'Ask 10 stargazing visitors or tour guides whether they would try a camel milk tasting box, what price they would pay, and what would make them trust it.'",
  "opportunity_score": {
    "local_fit": {"score": 4, "reason": "one line", "improve": "one suggestion to raise this score"},
    "clear_customer": {"score": 3, "reason": "one line", "improve": "one suggestion"},
    "low_starting_cost": {"score": 5, "reason": "one line", "improve": "one suggestion"},
    "easy_first_step": {"score": 4, "reason": "one line", "improve": "one suggestion"},
    "growth_potential": {"score": 3, "reason": "one line", "improve": "one suggestion"},
    "total": 19
  },
  "small_test_plan": {"intro": "one line", "points": ["point"]},
  "do_not_start_with": ["full license process before validating demand", "large stock purchase", "expensive marketing", "full website", "large production batch"],
  "instead_do": ["test with 10 people", "create a WhatsApp interest form", "collect pre-orders", "run a small pilot"],
  "seven_day_plan": [{"day": 1, "focus": "title", "action": "what to do", "output": "what you should have by end of day", "time_needed": "e.g. 1 hour", "success_check": "how to know it worked"}],
  "validation_before_spending": ["short point"],
  "validation_questions": ["question"],
  "whatsapp_message": "Hi, I am testing a small idea in Al Qua'a: [idea]. Before I spend money, I want to ask 3 quick questions. Would you try this if the price and quality were good?",
  "readiness_report": {"idea": "string", "target_customer": "string", "best_first_action": "string", "estimated_first_test_cost_aed": 200, "what_not_to_start_with": "string", "main_risk": "string", "first_customer_channel": "string", "next_step": "string"},
  "decision_engine": {"decision": "Run a small pilot | Validate more | Rework the idea", "reason": "one line tied to score and local fit", "next_test_action": "one concrete next action", "risk_level": "Low | Medium | High", "recommended_test_budget_aed": "300-500"},
  "customer_personas": [{"name": "persona name e.g. Stargazing tourist", "cares_about": "what they value", "reach_through": "how to reach them locally", "ask": "one question to ask them"}],
  "risk_radar": [{"name": "Demand risk", "level": "Low | Medium | High", "reason": "one line", "fix": "one line"}],
  "pitches": {"ten_sec": "10-second pitch", "thirty_sec": "30-second pitch", "whatsapp": "short WhatsApp pitch", "instagram": "Instagram caption"},
  "founder_passport": {"status": "e.g. Ready to test", "first_action": "short", "next_step": "short"},
  "steps": [{"step_number": 1, "action": "string", "description": "string", "estimated_cost_aed": 500, "timeline_days": 7, "who_to_contact": "string", "location": "string"}],
  "total_estimated_cost_aed": 5000,
  "total_timeline_days": 60,
  "first_customer_tip": "string"
}"""

USER_TYPE_HINTS = {
    "stargazing_visitors": "Channel: visitors, camping groups, tour guides. Risk: weekend/seasonal demand. Test: samples or pre-orders during visiting times.",
    "camel_farm_families": "Channel: farm owners, local families, suppliers. Risk: trust and supply consistency. Test: interview 10 farm owners.",
    "local_farmers": "Channel: neighbouring farms, suppliers, co-ops. Risk: seasonality and price. Test: ask 10 farmers what they repeatedly need.",
    "students": "Channel: schools, student groups, social media. Risk: low budgets. Test: small affordable offer to a student group.",
    "small_traders": "Channel: local shops, markets, resellers. Risk: margins. Test: sample batch to 5 shops.",
    "tourists": "Channel: tour operators, hotels, hotspots. Risk: seasonal flow. Test: small stand/pre-order at peak times.",
    "farm_workers": "Channel: workers, farm canteens, nearby housing. Risk: limited spending. Test: affordable items to 10 workers.",
    "al_quaa_residents": "Channel: neighbours, community groups, local WhatsApp. Risk: small population. Test: ask 10 residents directly.",
}


def build_prompt(lang, user_type):
    base = f"""You help FIRST-TIME founders in Al Ain and Al Qua'a (rural UAE) take their first real step, testing cheaply BEFORE spending the full budget.

Return ONLY a valid JSON object in exactly this structure, no extra text:
{SCHEMA}

Rules:
- first_step_today: MUST be specific and customer-facing (talk to real people, ask price/trust), doable today in under 2 hours, no license or setup. NOT vague like "research the market".
- seven_day_plan: exactly 7 entries; fill day, focus, action, output, time_needed, success_check for each. Focus on validation (define customer, ask 10 people, review price, WhatsApp/order test, prepare sample, test with 3-5, decide) NOT business setup.
- opportunity_score: rate each 1-5 with a one-line reason AND a one-line "improve" suggestion; total = sum (max 25). Score honestly based on idea specificity, customer type, budget, category, and local fit. Do not inflate.
- decision_engine: pick "Run a small pilot" (score >=20 or strong interest), "Validate more" (15-19 or unclear customer), or "Rework the idea" (<15 or weak demand). Give a reason, a concrete next_test_action, a risk_level (Low/Medium/High), and a small recommended_test_budget_aed range (e.g. "300-500").
- customer_personas: exactly 3, local to Al Qua'a / Al Ain when relevant (e.g. stargazing tourist, tour guide, camping organiser, farm family). Each with name, cares_about, reach_through, ask.
- risk_radar: exactly 5 entries named "Demand risk", "Cost risk", "Trust risk", "Legal risk", "Execution risk"; each with level (Low/Medium/High), one reason, one fix. For Legal risk, never assert exact requirements; say to verify with TAMM/ADDED/Abu Dhabi authorities.
- pitches: fill ten_sec, thirty_sec, whatsapp, instagram. Local, authentic, concise.
- founder_passport: status, first_action, next_step (short memorable summary).
- do_not_start_with / instead_do: keep them concrete and tied to Challenge 1 (test before spending).
- validation_questions: exactly 5.
- validation_before_spending: 3-4 short points.
- small_test_plan.points: 4-5 short points.
- steps: exactly 5 with real UAE context (ADDED, Khalifa Fund, DED Al Ain, TAMM, Basher). Costs in AED.
- judge_summary: fill all 6 fields including why_local (reference Al Qua'a camel farming / stargazing tourism where relevant).
- Use authentic local context where it fits: Al Qua'a, Al Ain, camel farms, stargazing tourism, rural families, farm workers, small traders, students, tourists.
- Frame UAE resources as suggestions to check; never assert exact legal requirements as certain.
- For evidence/claims, prefer honest "assumption to test" wording over unsupported "research shows" claims.
- estimated_first_test_cost_aed should be small (cost to validate, not to launch)."""
    if user_type and user_type in USER_TYPE_HINTS:
        base += f"\n\nTarget local user type: {user_type.replace('_',' ')}. Tailor accordingly. {USER_TYPE_HINTS[user_type]}"
    if lang == "ar":
        base += "\n\nWrite ALL text values in Arabic."
    return base


def call_groq(system, user, json_mode=True):
    body = {"model": MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.7, "max_tokens": 4000}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    resp = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json=body, timeout=40)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]



def _int(v, default=0):
    try:
        if isinstance(v, str):
            v = "".join(ch for ch in v if ch.isdigit() or ch == "-")
        return int(float(v)) if v not in (None, "", "-") else default
    except Exception:
        return default

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    lang = data.get("lang", "en")
    user_type = data.get("user_type", "")
    system = build_prompt(lang, user_type)
    user = f"Business idea: {data.get('idea','')}\nCategory: {data.get('category','')}\nBudget: {data.get('budget','')} AED\nLocation: Al Qua'a / Al Ain, UAE"
    try:
        text = call_groq(system, user, json_mode=True)
        return jsonify(json.loads(text))
    except Exception as e:
        print("GENERATE ERROR:", repr(e))
        return jsonify({"error": "generation_failed"}), 500


def _short_context(plan_context):
    """Trim the plan to a small summary so /ask never blows the token or rate limit."""
    try:
        p = json.loads(plan_context) if isinstance(plan_context, str) else (plan_context or {})
    except Exception:
        return str(plan_context)[:800]
    r = p.get("readiness_report", {}) or {}
    bits = {
        "idea": r.get("idea") or p.get("summary", ""),
        "target_customer": r.get("target_customer", ""),
        "first_step_today": p.get("first_step_today", ""),
        "main_risk": r.get("main_risk", ""),
        "first_customer_channel": r.get("first_customer_channel", ""),
    }
    return "; ".join(f"{k}: {v}" for k, v in bits.items() if v)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    lang = data.get("lang", "en")
    question = (data.get("question", "") or "").strip()
    if not question:
        return jsonify({"answer": "Please enter a question."}), 200

    context = _short_context(data.get("plan_context", ""))
    sys_lang = "Reply in Arabic." if lang == "ar" else "Reply in English."
    system = (
        "You are a helpful UAE business advisor for first-time founders in Al Qua'a / Al Ain. "
        f"The founder's plan summary: {context}. "
        "Answer their follow-up concisely and practically with LOCAL specifics. "
        "If asked how to find the first customer, give specific local channels (tour guides, camel farms, local WhatsApp groups, markets). "
        "If asked about risks, list 3-5 concrete risks and how to reduce each. "
        "If asked about pricing, suggest testing a price range with real customers before fixing it. "
        "For any legal, license, permit, or regulation question, do NOT state exact requirements as certain; say "
        "'Exact requirements depend on the activity and location. Check TAMM, ADDED, and the relevant Abu Dhabi authorities. This is guidance, not legal advice.' "
        f"{sys_lang} Keep it under 130 words."
    )

    if not API_KEY:
        print("ASK ERROR: API_KEY is empty")
        return jsonify({"answer": "The server has no API key configured. Add secret.txt or GROQ_API_KEY."}), 200

    try:
        answer = call_groq(system, question, json_mode=False)
        return jsonify({"answer": answer})
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        detail = ""
        try:
            detail = e.response.json().get("error", {}).get("message", "")
        except Exception:
            pass
        print(f"ASK HTTP ERROR {code}: {detail}")
        if code == 429:
            msg = ("الخدمة مشغولة الآن (تجاوز الحد). انتظر دقيقة وحاول مجدداً."
                   if lang == "ar" else
                   "The free AI service is rate-limited right now. Please wait a minute and try again.")
        else:
            msg = ("تعذّر الحصول على إجابة الآن. حاول مرة أخرى."
                   if lang == "ar" else
                   "Couldn't get an answer right now. Please try again.")
        return jsonify({"answer": msg}), 200
    except Exception as e:
        print("ASK ERROR:", repr(e))
        fallback = ("تعذّر الحصول على إجابة الآن. حاول مرة أخرى بعد قليل."
                    if lang == "ar" else
                    "Sorry, I couldn't get an answer right now. Please try again in a moment.")
        return jsonify({"answer": fallback}), 200


# ---------- PDF generation ----------
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
AMIRI_PATH = os.path.join(FONT_DIR, "Amiri-Regular.ttf")
_ARABIC_READY = None


def ensure_arabic_font():
    global _ARABIC_READY
    if _ARABIC_READY is not None:
        return _ARABIC_READY
    try:
        os.makedirs(FONT_DIR, exist_ok=True)
        if not os.path.exists(AMIRI_PATH):
            url = "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Regular.ttf"
            urllib.request.urlretrieve(url, AMIRI_PATH)
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        pdfmetrics.registerFont(TTFont("Amiri", AMIRI_PATH))
        _ARABIC_READY = True
    except Exception as e:
        print("Arabic font setup failed:", e)
        _ARABIC_READY = False
    return _ARABIC_READY


def shape_ar(text):
    """Reshape + bidi Arabic text so it renders correctly in PDF."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)


def _int(v, default=0):
    try:
        if isinstance(v, str):
            v = "".join(ch for ch in v if ch.isdigit() or ch == "-")
        return int(float(v)) if v not in (None, "", "-") else default
    except Exception:
        return default


def make_score_chart(sc, ar=False):
    """Horizontal bar chart of the 5 score categories -> PNG bytes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names_en = {"local_fit": "Local fit", "clear_customer": "Clear customer", "low_starting_cost": "Low start cost", "easy_first_step": "Easy first step", "growth_potential": "Growth potential"}
    keys = list(names_en.keys())
    vals = [_int((sc.get(k) or {}).get("score", 0)) for k in keys]
    labels = [names_en[k] for k in keys]
    fig, ax = plt.subplots(figsize=(5.2, 2.4), dpi=150)
    y = range(len(labels))
    ax.barh(list(y), vals, color="#378ADD", height=0.6)
    ax.set_xlim(0, 5)
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xticks([0,1,2,3,4,5])
    ax.tick_params(axis="x", labelsize=8)
    for i, v in enumerate(vals):
        ax.text(v + 0.1, i, f"{v}/5", va="center", fontsize=8, color="#1a1a2e")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    plt.tight_layout()
    b = io.BytesIO(); plt.savefig(b, format="png", bbox_inches="tight"); plt.close(fig); b.seek(0)
    return b


def make_steps_charts(steps):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = [f"Step {s.get('step_number','')}" for s in steps]
    days = [_int(s.get("timeline_days", 0)) for s in steps]
    costs = [_int(s.get("estimated_cost_aed", 0)) for s in steps]
    # timeline bar
    fig1, ax1 = plt.subplots(figsize=(2.9, 2.2), dpi=150)
    ax1.bar(labels, days, color="#378ADD")
    ax1.set_title("Timeline per step (days)", fontsize=9)
    ax1.tick_params(labelsize=7); plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")
    for s in ["top","right"]: ax1.spines[s].set_visible(False)
    plt.tight_layout(); b1=io.BytesIO(); plt.savefig(b1,format="png",bbox_inches="tight"); plt.close(fig1); b1.seek(0)
    # cost donut
    fig2, ax2 = plt.subplots(figsize=(2.9, 2.2), dpi=150)
    pal=["#534AB7","#1D9E75","#D85A30","#378ADD","#BA7517"]
    ax2.pie(costs if sum(costs)>0 else [1]*len(costs), colors=pal[:len(costs)], wedgeprops=dict(width=0.42))
    ax2.set_title("Cost breakdown (AED)", fontsize=9)
    plt.tight_layout(); b2=io.BytesIO(); plt.savefig(b2,format="png",bbox_inches="tight"); plt.close(fig2); b2.seek(0)
    return b1, b2


def build_pdf(p, lang="en"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                    PageBreak, Image, Frame, PageTemplate, BaseDocTemplate)
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT

    ar = (lang == "ar")
    font_ok = ensure_arabic_font() if ar else False
    BASE = "Amiri" if (ar and font_ok) else "Helvetica"
    BOLD = "Amiri" if (ar and font_ok) else "Helvetica-Bold"
    align = TA_RIGHT if ar else TA_LEFT

    def tx(s):
        return shape_ar(s) if ar else str(s)

    NAVY = colors.HexColor("#1a1a2e")
    BLUE = colors.HexColor("#378ADD")
    GREY = colors.HexColor("#666666")
    LIGHT = colors.HexColor("#f7f7f5")

    buf = io.BytesIO()

    def header_band(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1]-22*mm, A4[0], 22*mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(BOLD, 12)
        title = tx("StartSmart UAE — تقرير الخطوة الأولى") if ar else "StartSmart UAE — Founder First-Step Report"
        if ar:
            canvas.drawRightString(A4[0]-15*mm, A4[1]-14*mm, title)
        else:
            canvas.drawString(15*mm, A4[1]-14*mm, title)
        canvas.setFillColor(colors.HexColor("#cccccc"))
        canvas.setFont(BASE, 8)
        canvas.drawRightString(A4[0]-15*mm, 10*mm, f"{doc.page}")
        canvas.restoreState()

    doc = BaseDocTemplate(buf, pagesize=A4, topMargin=30*mm, bottomMargin=16*mm, leftMargin=16*mm, rightMargin=16*mm,
                          title="StartSmart UAE - Founder Report")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="band", frames=[frame], onPage=header_band)])

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", fontName=BOLD, textColor=NAVY, fontSize=20, leading=26, spaceAfter=8, alignment=align)
    sub = ParagraphStyle("sub", fontName=BASE, textColor=GREY, fontSize=11, leading=15, spaceAfter=14, alignment=align)
    h2 = ParagraphStyle("h2", fontName=BOLD, textColor=NAVY, fontSize=13, spaceBefore=10, spaceAfter=6, alignment=align)
    body = ParagraphStyle("body", fontName=BASE, fontSize=10, leading=15, spaceAfter=3, alignment=align)
    small = ParagraphStyle("small", fontName=BASE, fontSize=8.5, textColor=GREY, leading=12, alignment=align)

    L = {
        "en": dict(report="Founder First-Step Report", score="Opportunity score", decision="Decision",
                   exec="Executive summary", idea="Business idea", target="Target customer", first="First step today",
                   risk="Main risk", next="Next step", d7="First 7 days", day="Day", focus="Focus", action="Action",
                   vq="5 customer validation questions", wa="WhatsApp test message", stp="Small test plan before spending",
                   rr="Founder readiness report", best="Best first action", testcost="First test cost",
                   notstart="What not to start with", channel="First customer channel",
                   fuller="The fuller path (when you're ready)", total="Total cost", timeline="Timeline",
                   res="Suggested official resources to check",
                   note="This is guidance, not confirmed legal advice. Verify exact rules with the official authority.",
                   strong="Strong idea for a small first test.", medium="Possible idea, but needs more validation.",
                   weak="Needs more work before starting.",
                   deng="Founder decision", pm="Proof mode summary",
                   pm_int="Interested", pm_maybe="Maybe", pm_avg="Average price (AED)", pm_pre="Pre-orders",
                   pm_concern="Top concern", pm_none="No customer feedback entered yet. Use the 10-person test to validate demand.",
                   donot="Do not start with", instead="Instead, do this first", nexttest="Next test action", testbudget="Recommended test budget", bys="Before you spend", bys_plan="You are planning to spend", bys_test="Recommended first test", bys_save="Potential money protected", passport="Founder passport", pp_status="Status", pp_first="First action", personas="Customer personas", risks="Risk radar", pitches="Pitch ideas", cares="Cares about", reach="Reach through", ask="Ask"),
        "ar": dict(report="تقرير الخطوة الأولى للمؤسس", score="درجة الفرصة", decision="القرار",
                   exec="الملخص التنفيذي", idea="فكرة المشروع", target="العميل المستهدف", first="خطوتك الأولى اليوم",
                   risk="الخطر الرئيسي", next="الخطوة التالية", d7="أول 7 أيام", day="اليوم", focus="التركيز", action="الإجراء",
                   vq="5 أسئلة للتحقق من العملاء", wa="رسالة واتساب للاختبار", stp="خطة اختبار صغيرة قبل الإنفاق",
                   rr="تقرير جاهزية المؤسس", best="أفضل إجراء أول", testcost="تكلفة الاختبار الأول",
                   notstart="ما لا تبدأ به", channel="قناة أول عميل",
                   fuller="المسار الكامل (عندما تكون جاهزاً)", total="التكلفة الإجمالية", timeline="المدة",
                   res="مصادر رسمية مقترحة للمراجعة",
                   note="هذا إرشاد وليس استشارة قانونية مؤكدة. تحقق من القواعد مع الجهة الرسمية.",
                   strong="فكرة قوية لاختبار أولي صغير.", medium="فكرة ممكنة، لكنها تحتاج مزيداً من التحقق.",
                   weak="تحتاج مزيداً من العمل قبل البدء.",
                   deng="قرار المؤسس", pm="ملخص وضع الإثبات",
                   pm_int="مهتم", pm_maybe="ربما", pm_avg="متوسط السعر (درهم)", pm_pre="طلبات مسبقة",
                   pm_concern="أبرز قلق", pm_none="لم تُدخل ملاحظات العملاء بعد. استخدم اختبار الـ10 أشخاص للتحقق من الطلب.",
                   donot="لا تبدأ بـ", instead="بدلاً من ذلك، ابدأ بـ", nexttest="إجراء الاختبار التالي", testbudget="ميزانية الاختبار المقترحة", bys="قبل أن تنفق", bys_plan="أنت تخطط لإنفاق", bys_test="الاختبار الأول الموصى به", bys_save="المال المحتمل حمايته", passport="جواز المؤسس", pp_status="الحالة", pp_first="أول إجراء", personas="شخصيات العملاء", risks="رادار المخاطر", pitches="أفكار العرض", cares="يهتم بـ", reach="الوصول عبر", ask="اسأل"),
    }[lang if lang in ("en", "ar") else "en"]

    sc = p.get("opportunity_score", {}) or {}
    total = _int(sc.get("total", 0))
    decision = L["strong"] if total >= 20 else (L["medium"] if total >= 15 else L["weak"])
    r = p.get("readiness_report", {}) or {}

    def kv(rows):
        data = [[Paragraph(tx(k), ParagraphStyle("k", parent=body, fontName=BOLD)), Paragraph(tx(v) if v not in (None, "") else "-", body)] for k, v in rows]
        if ar:
            data = [[c2, c1] for c1, c2 in data]
            t = Table(data, colWidths=[None, 50*mm])
        else:
            t = Table(data, colWidths=[50*mm, None])
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LINEBELOW",(0,0),(-1,-2),0.4,colors.HexColor("#eeeeee")),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        return t

    E = []
    # ---- PAGE 1 ----
    E.append(Paragraph(tx(p.get("business_name_suggestion","")), h1))
    E.append(Paragraph(tx(p.get("summary","")), sub))
    # score block: number + chart side by side
    try:
        chart_img = Image(make_score_chart(sc, ar), width=110*mm, height=50*mm)
    except Exception as e:
        print("score chart failed:", e); chart_img = Paragraph("", body)
    score_para = Paragraph(f'<font size=30 color="#378ADD">{total} / 25</font><br/><br/><b>{tx(L["decision"])}:</b> {tx(decision)}', body)
    sb = Table([[score_para, chart_img]], colWidths=[55*mm, None]) if not ar else Table([[chart_img, score_para]], colWidths=[None, 55*mm])
    sb.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    E.append(Paragraph(tx(L["score"]), h2)); E.append(sb); E.append(Spacer(1,8))
    E.append(Paragraph(tx(L["exec"]), h2))
    E.append(kv([(L["idea"], r.get("idea") or p.get("summary","")),(L["target"], r.get("target_customer","")),
                 (L["first"], p.get("first_step_today","")),(L["risk"], r.get("main_risk","")),(L["next"], r.get("next_step",""))]))
    # decision engine card
    de = p.get("decision_engine", {}) or {}
    if de.get("decision"):
        E.append(Spacer(1,8))
        E.append(Paragraph(tx(L["deng"]), h2))
        extra = ""
        if de.get("risk_level"): extra += f'{tx(L["risk"])}: {tx(de.get("risk_level"))}  '
        if de.get("recommended_test_budget_aed"): extra += f'{tx(L["testbudget"])}: {tx(de.get("recommended_test_budget_aed"))} AED'
        dec_tbl = Table([[Paragraph(f'<b>{tx(de.get("decision",""))}</b><br/>{tx(de.get("reason",""))}<br/><font color="#666666">{tx(L["nexttest"])}: {tx(de.get("next_test_action",""))}</font><br/><font color="#666666">{extra}</font>', body)]], colWidths=[None])
        dec_tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#eef4ff")),
            ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#2f6fed")),("TOPPADDING",(0,0),(-1,-1),10),
            ("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10)]))
        E.append(dec_tbl)
    # Before You Spend card
    budget = _int(p.get("total_estimated_cost_aed", 0))
    test_cost = _int((p.get("readiness_report",{}) or {}).get("estimated_first_test_cost_aed", 0)) or 300
    protected = max(0, budget - test_cost)
    if budget > 0:
        E.append(Spacer(1,8)); E.append(Paragraph(tx(L["bys"]), h2))
        bys_tbl = Table([[Paragraph(f'{tx(L["bys_plan"])}: <b>{budget:,} AED</b><br/>{tx(L["bys_test"])}: <b>{test_cost:,} AED</b><br/><font color="#0a7a3c">{tx(L["bys_save"])}: <b>{protected:,} AED</b></font>', body)]], colWidths=[None])
        bys_tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#e7f8ee")),("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#1d9e75")),
            ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10)]))
        E.append(bys_tbl)
    # Founder Passport
    pp = p.get("founder_passport", {}) or {}
    E.append(Spacer(1,8)); E.append(Paragraph(tx(L["passport"]), h2))
    E.append(kv([
        (L["idea"], r.get("idea") or p.get("summary","")),
        (L["pp_status"], pp.get("status","Ready to test")),
        (L["pp_first"], pp.get("first_action") or p.get("first_step_today","")),
        (L["score"], f"{total} / 25"),
        (L["decision"], de.get("decision","")),
        (L["channel"], r.get("first_customer_channel","")),
        (L["testcost"], (f"{_int(r.get('estimated_first_test_cost_aed'))} AED" if r.get("estimated_first_test_cost_aed") not in (None,"") else "-")),
        (L["next"], pp.get("next_step") or r.get("next_step","")),
    ]))
    E.append(PageBreak())

    # ---- PAGE 2 ----
    E.append(Paragraph(tx(L["d7"]), h2))
    drows=[[Paragraph(tx(L["day"]),small),Paragraph(tx(L["focus"]),small),Paragraph(tx(L["action"]),small)]]
    for d in p.get("seven_day_plan",[]):
        drows.append([Paragraph(tx(d.get("day","")),small),Paragraph(tx(d.get("focus","")),small),Paragraph(tx(d.get("action","")),small)])
    if ar: drows=[list(reversed(r0)) for r0 in drows]
    dt=Table(drows,colWidths=([None,40*mm,14*mm] if ar else [14*mm,40*mm,None]))
    dt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)]))
    E.append(dt); E.append(Spacer(1,10))
    E.append(Paragraph(tx(L["vq"]), h2))
    for i,q in enumerate(p.get("validation_questions",[]),1):
        E.append(Paragraph(tx(f"{i}. {q}"), body))
    E.append(Spacer(1,8)); E.append(Paragraph(tx(L["wa"]), h2)); E.append(Paragraph(tx(p.get("whatsapp_message","")), body))
    E.append(Spacer(1,8)); tp=p.get("small_test_plan",{}) or {}
    E.append(Paragraph(tx(L["stp"]), h2))
    if tp.get("intro"): E.append(Paragraph(tx(tp["intro"]), body))
    for pt in tp.get("points",[]): E.append(Paragraph(tx(f"• {pt}"), body))
    E.append(PageBreak())

    # ---- PAGE 3: PROOF MODE SUMMARY ----
    E.append(Paragraph(tx(L["pm"]), h2))
    pm = p.get("proof_summary", {}) or {}
    if pm and _int(pm.get("total_responses", 0)) > 0:
        E.append(kv([
            (L["pm_int"], f"{_int(pm.get('interested'))}/{_int(pm.get('total_responses'))}"),
            (L["pm_maybe"], f"{_int(pm.get('maybe'))}/{_int(pm.get('total_responses'))}"),
            (L["pm_avg"], f"{_int(pm.get('avg_price'))} AED"),
            (L["pm_pre"], f"{_int(pm.get('pre_orders'))}/{_int(pm.get('total_responses'))}"),
            (L["pm_concern"], pm.get("top_concern","-")),
            (L["decision"], pm.get("verdict","-")),
        ]))
    else:
        E.append(Paragraph(tx(L["pm_none"]), body))
    E.append(PageBreak())

    # ---- PAGE 4: READINESS ----
    E.append(Paragraph(tx(L["personas"]), h2))
    for per in (p.get("customer_personas", []) or [])[:3]:
        E.append(Paragraph(f'<b>{tx(per.get("name",""))}</b>', body))
        E.append(Paragraph(f'{tx(L["cares"])}: {tx(per.get("cares_about",""))}', small))
        E.append(Paragraph(f'{tx(L["reach"])}: {tx(per.get("reach_through",""))}', small))
        E.append(Paragraph(f'{tx(L["ask"])}: {tx(per.get("ask",""))}', small))
        E.append(Spacer(1,4))
    E.append(Spacer(1,6)); E.append(Paragraph(tx(L["risks"]), h2))
    rr_rows=[[Paragraph(tx(L["risk"]),small),Paragraph(tx(L["pp_status"]),small),Paragraph(tx(L["cares"]),small),Paragraph(tx(L["instead"]),small)]]
    for rk in (p.get("risk_radar", []) or []):
        rr_rows.append([Paragraph(tx(rk.get("name","")),small),Paragraph(tx(rk.get("level","")),small),Paragraph(tx(rk.get("reason","")),small),Paragraph(tx(rk.get("fix","")),small)])
    if len(rr_rows) > 1:
        if ar: rr_rows=[list(reversed(r0)) for r0 in rr_rows]
        rrt=Table(rr_rows,colWidths=([None,18*mm,42*mm,42*mm] if ar else [28*mm,18*mm,52*mm,None]))
        rrt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)]))
        E.append(rrt)
    E.append(PageBreak())

    # ---- PAGE 5: READINESS ----
    E.append(Paragraph(tx(L["rr"]), h2))
    E.append(kv([(L["idea"],r.get("idea","")),(L["target"],r.get("target_customer","")),(L["best"],r.get("best_first_action","")),
                 (L["testcost"],(f"{_int(r.get('estimated_first_test_cost_aed'))} AED" if r.get("estimated_first_test_cost_aed") not in (None,"") else "-")),
                 (L["notstart"],r.get("what_not_to_start_with","")),(L["risk"],r.get("main_risk","")),
                 (L["channel"],r.get("first_customer_channel","")),(L["next"],r.get("next_step",""))]))
    dns = p.get("do_not_start_with", []) or []
    ins = p.get("instead_do", []) or []
    if dns:
        E.append(Spacer(1,8)); E.append(Paragraph(tx(L["donot"]), h2))
        for x in dns: E.append(Paragraph(tx(f"\u2717 {x}"), body))
    if ins:
        E.append(Spacer(1,6)); E.append(Paragraph(tx(L["instead"]), h2))
        for x in ins: E.append(Paragraph(tx(f"\u2713 {x}"), body))
    E.append(PageBreak())

    # ---- PAGE 5: FULLER PATH ----
    E.append(Paragraph(tx(L["fuller"]), h2))
    E.append(Paragraph(tx(f"{L['total']}: {_int(p.get('total_estimated_cost_aed',0)):,} AED    {L['timeline']}: {p.get('total_timeline_days','')} {('يوم' if ar else 'days')}"), body))
    E.append(Spacer(1,6))
    try:
        c1,c2=make_steps_charts(p.get("steps",[]))
        imgs=Table([[Image(c1,width=80*mm,height=58*mm),Image(c2,width=80*mm,height=58*mm)]])
        imgs.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
        E.append(imgs); E.append(Spacer(1,8))
    except Exception as e:
        print("steps charts failed:",e)
    srows=[[Paragraph(tx("#"),small),Paragraph(tx(L["action"]),small),Paragraph(tx("AED"),small),Paragraph(tx(L["day"]),small)]]
    for s in p.get("steps",[]):
        srows.append([Paragraph(tx(s.get("step_number","")),small),
            Paragraph(f'<b>{tx(s.get("action",""))}</b><br/>{tx(s.get("description",""))}',small),
            Paragraph(f"{_int(s.get('estimated_cost_aed',0)):,}",small),Paragraph(tx(s.get("timeline_days","")),small)])
    if ar: srows=[list(reversed(r0)) for r0 in srows]
    st=Table(srows,colWidths=([14*mm,22*mm,None,10*mm] if ar else [10*mm,None,22*mm,14*mm]))
    st.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)]))
    E.append(st); E.append(Spacer(1,10))
    E.append(Paragraph(tx(L["res"]), h2))
    for nm in ["TAMM — tamm.abudhabi","Khalifa Fund — khalifafund.ae","ADDED — added.gov.ae","Bashr / Basher — basher.gov.ae"]:
        E.append(Paragraph(tx(f"• {nm}"), body))
    E.append(Spacer(1,8)); E.append(Paragraph(tx(L["note"]), small))

    doc.build(E)
    buf.seek(0)
    return buf


@app.route("/pdf", methods=["POST"])
def pdf():
    from flask import send_file
    p = request.json or {}
    lang = p.get("_lang", "en")
    try:
        buf = build_pdf(p, lang)
    except Exception as e:
        print("PDF BUILD ERROR:", repr(e))
        return jsonify({"error": "pdf_failed"}), 500
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="StartSmart_UAE_Founder_Report.pdf")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
