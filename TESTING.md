# StartSmart UAE — Testing Checklist

Run through this before submitting. Tick each item.

## Core flow
- [ ] App opens at http://127.0.0.1:5000 without errors
- [ ] Empty input is handled (button does nothing on blank idea)
- [ ] Demo example buttons fill the idea box
- [ ] Category and customer-type dropdowns are populated
- [ ] "Get my first step" shows the loader, then results
- [ ] Judge summary card appears with all fields
- [ ] First Step Today is specific and customer-facing

## Opportunity score
- [ ] Gauge animates and shows the total /25
- [ ] Five categories show score, reason, and improvement tip
- [ ] Interpretation line matches the score band

## Decision engine
- [ ] Decision card shows a clear verdict, reason, and next test action

## Proof Mode
- [ ] Table shows 10 rows
- [ ] "Fill demo feedback" populates realistic data
- [ ] Interest count, average price, pre-orders update
- [ ] Verdict changes based on the data
- [ ] "Download data (CSV)" downloads a CSV
- [ ] "Clear" resets the table

## What not to do
- [ ] "Do not start with" and "Instead" lists both appear

## WhatsApp
- [ ] Message includes the business idea
- [ ] "Copy" copies the message (paste to confirm)
- [ ] "Open WhatsApp" opens wa.me with the message
- [ ] Works on local IP (192.168.x.x:5000)

## Follow-up questions
- [ ] Ask 3 questions in a row — all answers appear, no crash
- [ ] License question uses safe wording ("verify with the authority")

## Shareable summary
- [ ] Summary text generates and Copy works

## PDF
- [ ] "Download PDF" produces StartSmart_UAE_Founder_Report.pdf
- [ ] PDF is a clean report (no buttons, inputs, empty rows, or URL)
- [ ] Includes: exec summary, first step, score, decision, 7-day, questions,
      WhatsApp message, proof summary, readiness, resources, legal note
- [ ] Proof summary page shows data if entered, else a clear placeholder

## Arabic
- [ ] العربية flips the whole interface to Arabic + RTL
- [ ] All new sections are translated
- [ ] Arabic PDF downloads and shows readable right-to-left Arabic

## Dark mode
- [ ] Moon button toggles dark mode and back

## Mobile
- [ ] Layout readable on a phone width
- [ ] Proof Mode table scrolls horizontally, no page overflow
- [ ] Buttons are tappable and not overlapping

## Repo
- [ ] No API key committed (secret.txt is gitignored)
- [ ] requirements.txt is complete
- [ ] README has names, live URL, and video link filled in

## Polish pass (v3) additions
- [ ] Hero shows waving UAE flag, 3 feature chips, and the Al Qua'a badge
- [ ] Score of 20+ triggers confetti (flag colors)
- [ ] Proof Mode stat numbers animate (count up)
- [ ] Decision card shows risk level and recommended test budget
- [ ] "Why Al Qua'a?" card appears with local context items
- [ ] Trust badges row appears (no login, no payment, etc.)
- [ ] Premium footer shows UAE flag + Abu Dhabi University
- [ ] Reduced-motion setting disables animations and confetti
- [ ] No horizontal scroll on a 390px phone width


## Feature pass (v6) additions
- [ ] Bashr / Basher link opens basher.gov.ae (plus u.ae backup link)
- [ ] All UAE resource links open in a new tab
- [ ] Hero preview card shows on desktop (score / decision / next action)
- [ ] Judge Mode button steps through sections with highlight; safe on re-click
- [ ] Founder Passport renders 8 fields; Copy works; appears in PDF
- [ ] Before You Spend shows budget, test cost, money protected (never negative)
- [ ] Customer Personas show 3 cards
- [ ] Risk Radar shows 5 risks with levels and fixes
- [ ] Pitch Generator shows 4 pitches, each Copy works
- [ ] Local Opportunity Map shows the flow
- [ ] Validation QR code renders (or shows a safe link fallback)
- [ ] Fill demo feedback animates customer-by-customer
- [ ] Advisor never shows a rate-limit message (local fallback)
- [ ] PDF includes passport, before-you-spend, personas, risk radar
- [ ] All new sections work in Arabic
- [ ] No console errors after a full run
