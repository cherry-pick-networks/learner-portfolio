# Phase 1 SharePoint Lists — Column Schema

Lists are split across two sub sites: **syllabus-corpus** (tutor ops & content) and **syllabus-learner** (learner roster & progress). Column names and types must match so Power Automate and Copilot Studio can bind correctly. Terminology follows Cambridge ELT (grammar, lexis, phonology; American spelling).

**Level (CEFR):** All level columns in M365 use CEFR. Picker internal levels map as follows:

| picker level | CEFR |
|--------------|------|
| basic | A1 / A2 |
| intermediate | B1 / B2 |
| advanced | C1 / C2 |

---

## Naming conventions

**Column structure**

Columns are 1-word or 2-word (`word1_word2`). No column exceeds two words.

- **1-word columns** use a Cambridge ELT term directly.
- **2-word columns** use a qualifier (word 1) + attribute name (word 2). Word 1 must be a noun or established Cambridge ELT term that narrows the column's scope.

**Controlled qualifiers** — word 1 with enumerated allowed values:

| Qualifier | Allowed values |
|-----------|---------------|
| `cefr_` | `A1 \| A2 \| B1 \| B2 \| C1 \| C2` |
| `english_` | skills: `reading \| writing \| listening \| speaking`; systems: `grammar \| lexis \| phonology` |

**Descriptive qualifiers** — word 1 is a contextual noun; values are freeform. Examples: `learner_`, `task_`, `outcome_`, `lexical_`, `skill_`, `feedback_`, `acquisition_`.

**Suffix**

| Suffix | Applied to |
|--------|------------|
| `_at` | Timestamps |
| `_text` | Free-text input |
| `_id` | Entity identifiers |
| `_ref` | Loose references (codes, item IDs) |

**Cambridge terms (1-word columns):** `content`, `grammar`, `lexis`, `organization`, `item`

---

## 1. writing_assessment

> Site: **syllabus-corpus**

Stores AES (Automated Essay Scoring) results for essay drills.

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| session_at | Date and time | Yes | Yes |
| task_ref | Single line of text | No | No |
| content | Number | Yes | No |
| grammar | Number | Yes | No |
| lexis | Number | Yes | No |
| organization | Number | Yes | No |
| english_total | Number | Yes | No |
| cefr_writing | Single line of text | No | No |
| feedback_text | Multiple lines of text | No | No |
| answer_text | Multiple lines of text | No | No |

`cefr_writing` values: `A1 \| A2 \| B1 \| B2 \| C1 \| C2` (derived from total score; see 03-aes-anchor-essays.md)

Keep default **Title** column; you can rename it to `assessment_id` or leave as-is and use ID for references.

---

## 2. task_outcome

> Site: **syllabus-corpus**

Stores per-learner outcome records (worksheet answers, drill results). In Phase 1 you may add rows manually; later Recall/Forms will create them.

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| session_at | Date and time | Yes | Yes |
| task_ref | Single line of text | No | No |
| outcome_correct | Yes/No | No | No |
| answer_text | Multiple lines of text | No | No |
| english_skills | Single line of text | No | No |
| english_systems | Single line of text | No | No |

`english_skills` values: `reading \| writing \| listening \| speaking`

`english_systems` values: `grammar \| lexis \| phonology`

---

## 3. lexis_practice

> Site: **syllabus-learner**

Tracks per-learner lexis practice history (FSRS scheduling anchor).

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| lexical_item | Single line of text | Yes | No |
| cefr_level | Single line of text | No | No |
| practice_at | Date and time | No | No |

`cefr_level` values: `A1 \| A2 \| B1 \| B2 \| C1 \| C2`

---

## 4. lexis_acquisition

> Site: **syllabus-learner**

Tracks per-learner lexis acquisition state.

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| lexical_item | Single line of text | Yes | No |
| acquisition_stage | Single line of text | No | No |
| frequency | Number | No | No |

`frequency` values: NGSL rank 1–2800; AWL items use a separate range starting at 3000.

---

## 5. grammar_practice

> Site: **syllabus-learner**

Tracks per-learner grammar practice history (EGP guideword as item anchor).

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| grammar_item | Single line of text | Yes | No |
| cefr_level | Single line of text | No | No |
| practice_at | Date and time | No | No |

`grammar_item` values: grammar_profile guideword (e.g., `FORM: PRESENT PERFECT`). Source: grammar_profile reference data in text-extraction.

`cefr_level` values: `A1 \| A2 \| B1 \| B2 \| C1 \| C2`

---

## 6. grammar_acquisition

> Site: **syllabus-learner**

Tracks per-learner grammar acquisition state.

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| grammar_item | Single line of text | Yes | No |
| acquisition_stage | Single line of text | No | No |

---

## 7. phonology_practice

> Site: **syllabus-learner**

Tracks per-learner phonology practice history (word-level, ARPAbet anchor).

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| phonology_item | Single line of text | Yes | No |
| arpabet_ref | Single line of text | No | No |
| cefr_level | Single line of text | No | No |
| practice_at | Date and time | No | No |

`phonology_item` values: target word (e.g., `hello`).

`arpabet_ref` values: ARPAbet phoneme string generated by g2p-en (e.g., `HH AH0 L OW1`). Escape quotes/commas when used in Power Automate conditions.

`cefr_level` values: `A1 \| A2 \| B1 \| B2 \| C1 \| C2`

---

## 8. phonology_acquisition

> Site: **syllabus-learner**

Tracks per-learner phonology acquisition state.

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| phonology_item | Single line of text | Yes | No |
| acquisition_stage | Single line of text | No | No |

---

## 9. needs_analysis

> Site: **syllabus-learner**

Level-based English area weights for learner needs analysis (Cambridge CELTA concept; Phase 1 optional).

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| cefr_level | Single line of text | Yes | No |
| english_skills | Single line of text | No | No |
| english_systems | Single line of text | No | No |
| skill_weight | Number | Yes | No |

`english_skills` values: `reading \| writing \| listening \| speaking`

`english_systems` values: `grammar \| lexis \| phonology`

---

## 10. learner_proficiency

> Site: **syllabus-learner**

Per-learner CEFR proficiency per skill. One row per learner; update when reassessed.

| Column name | SharePoint type | Required | Indexed |
|-------------|-----------------|----------|---------|
| learner_id | Single line of text | Yes | Yes |
| cefr_reading | Single line of text | No | No |
| cefr_writing | Single line of text | No | No |
| cefr_listening | Single line of text | No | No |
| cefr_speaking | Single line of text | No | No |
| assessment_at | Date and time | No | No |

All `cefr_*` values: `A1 \| A2 \| B1 \| B2 \| C1 \| C2`

---

## Creation steps (SharePoint)

**On syllabus-learner:** Site contents → New → List → Blank list. Create **lexis_practice**, **lexis_acquisition**, **grammar_practice**, **grammar_acquisition**, **phonology_practice**, **phonology_acquisition**, **learner_proficiency**, and (when ready) **needs_analysis**. Add columns per tables above. Index `learner_id` on all lists.

**On syllabus-corpus:** Site contents → New → List → Blank list. Create **writing_assessment** and **task_outcome**. Add columns per tables above. For both lists: List settings → Indexed columns → Create a new index on `learner_id` (and optionally `session_at`) to keep views and flows fast as data grows.
