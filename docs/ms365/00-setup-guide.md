# M365 Phase 1 — Setup Guide

Follow these steps in order. All paths are menu or UI labels you can follow without screenshots.

---

## 1. Create SharePoint sites (in order)

1. Go to [sharepoint.com](https://sharepoint.com) and sign in with your M365 account.
2. **Create the hub site first:** Click **Create site** → **Communication site**. Choose template **Learning central**. Name: `syllabus`. Description: `tutor ops hub — multi-subject content, learner data & ai instruction`. Finish creation.
3. **Register `syllabus` as a Hub site:** Go to the **SharePoint admin center** ([admin.microsoft.com](https://admin.microsoft.com) → SharePoint → Sites → Active sites). Find `syllabus`, select it, and click **Hub** → **Register as hub site**. Give it the hub name `syllabus`.
4. **Create sub site 1:** **Create site** → **Team site**. Template: **IT help desk**. Name: `syllabus-learner`. Description: `learner roster & progress — level tracking, schedules & learning records`. After creation, associate it with the **syllabus** hub: go to the site → **Settings** (gear icon) → **Site information** → **Hub site association** → select `syllabus`.
5. **Create sub site 2:** **Create site** → **Team site**. Template: **Training design team**. Name: `syllabus-corpus`. Description: `tutor ops & content — worksheets, assessments & ai-assisted instruction`. Associate with the **syllabus** hub the same way.
6. Note the site URLs (e.g. `.../sites/syllabus`, `.../sites/syllabus-learner`, `.../sites/syllabus-corpus`).

---

## 2. Create Phase 1 lists

Lists are split across two sub sites. Use **[01-lists-phase1-schema.md](01-lists-phase1-schema.md)** for column definitions.

**On site `syllabus-learner`:**
1. **Site contents** → **New** → **List** → **Blank list**.
2. Create lists **lexis_practice**, **lexis_acquisition**, **grammar_practice**, **grammar_acquisition**, **phonology_practice**, **phonology_acquisition**, and **learner_proficiency**. Add columns per schema; add index on `learner_id` for all lists.

**On site `syllabus-corpus`:**
1. **Site contents** → **New** → **List** → **Blank list**.
2. Create lists **writing_assessment** and **task_outcome** with **exact** names.
3. For each list, add the columns described in the schema. For **writing_assessment** and **task_outcome**, add an index on `learner_id` (and optionally `session_at`): **List settings** → **Indexed columns** → **Create new index**.

---

## 3. Open Copilot Studio and create agents

### Agent A — Worksheet

1. Go to [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) and sign in.
2. **Create** → **New agent** → **Create from blank**. Name it (e.g. `Worksheet`).
3. Open **Instructions**. Copy the Instructions block from **[02-agent-worksheet.md](02-agent-worksheet.md)** and paste. Save.
4. **Knowledge**: Add a knowledge source. Choose **SharePoint** and select **syllabus-corpus**. Add the following files (upload to that site first if needed):
   - **ngsl-2800.csv** — Download from [newgeneralservicelist.org](https://www.newgeneralservicelist.org/). Export or save as CSV and upload to **syllabus-corpus**.
   - **awl-570.csv** — Optional. Search for "Coxhead Academic Word List" or "AWL 570 CSV". Upload to **syllabus-corpus** when ready.
5. **Actions** (optional for first test): When ready to save task outcomes, create a Power Automate flow per **[02-agent-worksheet.md](02-agent-worksheet.md)** and add it as an Action.

### Agent B — AES

1. **Create** → **New agent** → **Create from blank**. Name it (e.g. `Essay Scoring`).
2. Open **Instructions**. Copy the Instructions block from **[02-agent-aes.md](02-agent-aes.md)** and paste. Save.
3. **Knowledge**: Add **aes-anchor-essays.md** — Use **[03-aes-anchor-essays.md](03-aes-anchor-essays.md)**. Upload to **syllabus-corpus** or paste content into a Copilot Studio knowledge item.
4. **Actions**: Create a Power Automate flow per **[02-agent-aes.md](02-agent-aes.md)** and add it as an Action.

---

## 4. Vocabulary files (NGSL, AWL)

Upload all vocabulary files to **syllabus-corpus** (or add as Copilot Knowledge pointing to that site).

- **NGSL 2,800:** Download from [newgeneralservicelist.org](https://www.newgeneralservicelist.org/). Use the NGSL 1.01 or 2.0 word list; export or save as CSV (word, rank or similar).
- **AWL 570 (Coxhead):** Search for "Coxhead Academic Word List" or "AWL 570 CSV". Common source: Victoria University of Wellington pages or academic word list repositories. Save as CSV and upload. Used only when you ask the agent for B2+ or academic vocabulary.

---

## 5. needs_analysis (Phase 1 optional)

The **needs_analysis** list stores level-based skill-area weights for analytics (Cambridge CELTA concept; Phase 1 optional). When you are ready:

1. On site **syllabus-learner**, create a list named **needs_analysis** with columns such as: cefr_level (A1 | A2 | B1 | B2 | C1 | C2), english_skills (reading | writing | listening | speaking), english_systems (grammar | lexis | phonology), skill_weight (Number).
2. Fill initial rows with teacher estimates; later phases can update from real data.

---

## 6. Quick test

**Agent A (Worksheet):**
1. In Copilot Studio, open the Worksheet agent and go to **Test**.
2. Send: "Make a vocabulary worksheet with 10 words, A2 level."
3. You should get a markdown table with problems and an answer key at the end.

**Agent B (AES):**
1. Open the Essay Scoring agent and go to **Test**.
2. Send: "Score this essay: I like summer. I go swim. Weather is hot." You should get a JSON score with keys: content, grammar, lexis, organization, english_total, cefr_writing, feedback_text. If you connected the SaveEssayOutcome action, the flow will run (ensure learner_id and session_at are provided or set in the flow).

---

## File reference (this repo)

| File | Purpose |
|------|--------|
| [00-setup-guide.md](00-setup-guide.md) | This guide |
| [01-lists-phase1-schema.md](01-lists-phase1-schema.md) | Column definitions for all Phase 1 lists |
| [02-agent-worksheet.md](02-agent-worksheet.md) | Instructions + Knowledge/Action notes for Agent A (Worksheet) |
| [02-agent-aes.md](02-agent-aes.md) | Instructions + Knowledge/Action notes for Agent B (AES) |
| [03-aes-anchor-essays.md](03-aes-anchor-essays.md) | Rubric and anchor essays for AES; upload as Knowledge |
