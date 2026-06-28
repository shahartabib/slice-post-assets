# Slice Marketing Dept — Cloud Routine (REST, runs computer-OFF)

This repo is the working repo for a **Claude Code Cloud Routine** that runs server-side on
Anthropic infrastructure (laptop can be closed). It prepares next week's 3 social posts as
**drafts** in Marky and drafts replies to new Prosp conversations — it never schedules,
publishes, or sends anything. A human (Shahar) reviews and triggers everything.

Why REST and not MCP: Cloud Routines cannot run local stdio MCP servers (the `marky` and
`prosp` MCPs are local). So this routine calls the Marky and Prosp REST APIs directly.

---

## ONE-TIME SETUP

### 1. Repo prerequisites (this repo — commit before first run)
- `slice_fill.py` — cloud-portable PIL image filler (✅ in repo).
- `templates/` — 6 clean brand templates (✅ in repo): DataGrid.png, case study.png,
  Testimonial.png, Photo Overlay.png, Grid.png, SK_post_hero_45_clean.png.
- `fonts/` — **ADD MANUALLY**: drop `Archivo-Black.ttf` and `Archivo-SemiBold.ttf`
  (Google Fonts, free/OFL — https://fonts.google.com/specimen/Archivo) for the closest match
  to the Segoe UI Black/Semibold brand look. Without them the routine falls back to DejaVu
  (still works, lower fidelity). NOTE: do NOT commit Windows Segoe UI fonts to this public
  repo — their license forbids redistribution.
- `post-log.csv` — cloud log, replaces the OneDrive xlsx (✅ in repo, header only).
- `drafts/` — caption files + Prosp reply drafts land here (✅ in repo).
- (Optional) `calendar.md` — paste the 6-week calendar / specific weekly topics from
  `תוכנית_שיווק_סלייס_2026.docx`. If present the routine uses it; if absent it rotates pillars.

### 2. Create the routine
Go to **claude.ai/code → Routines** (`claude.ai/code/routines`) → New routine.
- **Repository:** `shahartabib/slice-post-assets`, branch `main`.
- **Trigger:** Schedule → Weekly, Sunday morning (e.g. 08:23 local).
- **Prompt:** paste the entire "ROUTINE PROMPT" block below.

### 3. Environment variables (routine settings → Environment)
- `MARKY_API_KEY` = `mk_live_...`  (from `שיווק סלייס/כלי שיווק/Marky API.txt`)
- `MARKY_BUSINESS_ID` = `e1db849d-f9c8-410d-ac24-ddf45f0f8ea6`
- `PROSP_API_KEY` = the bare UUID (from `שיווק סלייס/כלי שיווק/Prosp API.txt`)

### 4. Network access (routine settings → Environment → Network access)
Change from **Trusted** to **Custom** and add allowed domains:
- `api.mymarky.ai`
- `prosp.ai`
- `raw.githubusercontent.com`
(github.com + pypi are already on the default allowlist for git push and `pip install Pillow`.)

### 5. First run
Click **Run now** once and watch it. Fix any auth/allowlist errors, then let the schedule take over.

---

## DRAFT-ONLY vs AUTO-SCHEDULE (the one switch)
This routine is DRAFT-ONLY: it creates Marky posts with `status: "NEW"` (unscheduled drafts)
and never calls schedule/publish. To upgrade to fully autonomous (publishes computer-off),
change the Marky create call to `status: "SCHEDULED"` + `adhoc_publish_time: "<ISO>"`
(Sun 19:30 / Tue 15:00 / Thu 15:00 Israel time, i.e. `+03:00`). Do this only once you trust
the output — posts go public under Shahar's name.

---

## ROUTINE PROMPT  (paste everything below into the routine)

You are running Slice's autonomous marketing department, in DRAFT-ONLY mode, on a weekly
schedule. You run server-side in a clone of the `shahartabib/slice-post-assets` repo. You have
no access to OneDrive — all inputs/outputs are in this repo or the Marky/Prosp REST APIs.

HARD GUARDRAILS — never violate:
- Never schedule or publish a Marky post (create with status "NEW" only; never call
  /schedule or /publish; never use status "SCHEDULED").
- Never send a Prosp message (no /leads/send-message, /leads/send-voice). Read + draft only.
- Never start/stop a Prosp campaign, never delete anything.
- Report failures honestly; never claim something was posted/scheduled/sent.

SECRETS (from env): MARKY_API_KEY, MARKY_BUSINESS_ID, PROSP_API_KEY.

=== STEP A — DRAFT NEXT WEEK'S 3 POSTS ===
Cadence: 3 posts/week — Sun = Facebook, Hebrew; Tue = LinkedIn, English; Thu = LinkedIn, English.
Brand = Slice as the "agentic workspace for business outcomes" (displacing LMS/KMS). Tone:
eye-level, professional, no emojis, no sales language, no self-promotion. Hebrew (FB) must be
RTL and right-aligned and end with a reflective question. English (LinkedIn) is professional and
ends with a reflective prompt, not a CTA. Content pillars to rotate across weeks:
1) The gap (L&D/KMS stats vs. reality)  2) Outcomes over content (business results)
3) Agentic workspace vs. LMS/LXP/KMS  4) Customer outcome / case-study angle
5) Personalization & "knowledge that knows your people"  6) The future of enterprise work.

1. Read `calendar.md` if it exists for this week's specific topics; otherwise pick the next
   pillar(s) not used in recent `post-log.csv` rows. Read `post-log.csv` to find the next week
   whose Sun/Tue/Thu slots are not yet present, and to avoid repeating topics. Use today's real
   date to compute that week's Sunday/Tuesday/Thursday calendar dates.
2. For each of the 3 slots:
   a. CAPTION — write the post text for the right channel/language/tone. Save to
      `drafts/<DDMMYY><FB|LI>.md` (FB for the Sunday Hebrew post, LI for the LinkedIn posts).
   b. IMAGE — `pip install Pillow` if needed. Write a short driver that imports the fill_*
      functions from `slice_fill.py` and produces a PNG into `images/` with a unique name like
      `<DDMMYY><LI|FB>.png`. Pick the template that fits: datagrid for stat posts, casestudy for
      outcome/case posts, testimonial for quotes, headline (Photo Overlay/Grid) for statements.
   c. The public raw URL of each image is
      `https://raw.githubusercontent.com/shahartabib/slice-post-assets/main/images/<file>.png`.
   d. CREATE THE MARKY DRAFT (no scheduling): 
      POST https://api.mymarky.ai/api/posts
      Headers: Authorization: Bearer <MARKY_API_KEY> ; Content-Type: application/json
      Body: {"business_id":"<MARKY_BUSINESS_ID>","caption":"<text>",
             "publish_to":["facebook"] for the Sunday post / ["linkedInProfile"] for LinkedIn posts,
             "media_urls":["<raw image URL>"], "status":"NEW"}
      Capture the returned post id.
   e. Append a row to `post-log.csv`:
      date,week,channel,language,persona,pillar,topic,caption_file,image_url,status,marky_post_id,notes
      with status "DRAFT".
3. Commit and push images + captions + post-log.csv to `main` so the raw URLs resolve and the
   log persists. (Verify each raw URL returns HTTP 200 image/png after the push.)

=== STEP B — DRAFT PROSP REPLIES ===
All Prosp calls: POST to https://prosp.ai<path>, Content-Type: application/json, and include
"api_key": <PROSP_API_KEY> in the JSON body.
1. POST /api/v1/campaigns/lists  body {"api_key":...}  → get campaigns. Focus on the active
   Slice-relevant ones (e.g. names containing learnin / instructional designer / HR / EdTech).
2. For each, POST /api/v1/campaigns/leads  body {"api_key":...,"campaign_id":"<id>"} to list leads.
3. For leads that appear to have replied, POST /api/v1/leads/conversation
   body {"api_key":...,"linkedin_url":"<url>"} to read the thread. Identify NEW inbound messages
   (since the previous run — use the last run's drafts file / log as reference if available).
4. For each new reply, draft a short, human, consultative response in Shahar's voice (no hard
   pitch). DO NOT SEND. Write them all to `drafts/prosp_replies_<YYYY-MM-DD>.md`, one section per
   lead: name, campaign, their message, your drafted reply, LinkedIn URL.
5. Commit and push the drafts file.

=== FINAL OUTPUT ===
Report concisely: which week was drafted; the 3 caption files + 3 image raw URLs + 3 Marky draft
post ids (note: DRAFTS — not scheduled); how many new Prosp replies were drafted and the drafts
file path; and any step that failed. Remind Shahar: to publish, open Marky and schedule each
draft (linkedInProfile for LinkedIn, facebook for FB); review Prosp drafts before sending.
