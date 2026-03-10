# AES Anchor Essays — Copilot Studio Knowledge

Use this document as the scoring reference for Automated Essay Scoring. Each axis is 1–4 points; total 4–16.

## Rubric (1–4 per axis)

| Axis | 1 | 2 | 3 | 4 |
|------|---|---|---|---|
| **Grammar** | Many grammar/spelling errors; meaning unclear | Several errors; meaning mostly clear | Few errors; clear meaning | Correct or near-correct; natural |
| **Lexis** | Very limited; wrong word choice often | Basic words only; some misuse | Varied; few misuse | Varied and appropriate |
| **Organization** | No clear order; hard to follow | Some order; gaps in logic | Clear order; minor gaps | Clear order; logical flow |
| **Content** | Off-topic or too short | Partly on topic; incomplete | On topic; adequate length | Fully on topic; complete |

## Score → CEFR mapping

Derive `cefr_writing` from the total score (4–16). Use this table when producing AES output.

| Total score | CEFR | Picker level |
|-------------|------|--------------|
| 4–6 | A1 | basic |
| 7–8 | A2 | basic |
| 9–10 | B1 | intermediate |
| 11–12 | B2 | intermediate |
| 13–14 | C1 | advanced |
| 15–16 | C2 | advanced |

---

## Prompt (example for calibration)

**Task:** Write about your favorite season in 3–5 sentences. Say why you like it and what you do then.

---

## Basic — Anchor 1 (Score: 5/16)

Grammar 1, Lexis 1, Organization 2, Content 1

I like summer. I go swim. Weather is hot. I eat ice cream. My friend come my house. We play.

---

## Basic — Anchor 2 (Score: 7/16)

Grammar 2, Lexis 2, Organization 2, Content 1

My favorite season is summer. I like summer because is hot and I can swimming. In summer I go to beach with family. We have fun. Sometime we eat watermelon. I very like summer.

---

## Intermediate — Anchor 1 (Score: 10/16)

Grammar 2, Lexis 3, Organization 2, Content 3

I like autumn the most. The weather is not too hot and not too cold. The leaves change color and the sky is clear. I usually go hiking with my family on weekends. We take photos and have a picnic. Autumn makes me feel calm and happy. I think it is the best season for outdoor activities.

---

## Intermediate — Anchor 2 (Score: 11/16)

Grammar 3, Lexis 3, Organization 3, Content 2

My favorite season is spring. In spring the flowers bloom and the days get longer. I enjoy walking in the park and seeing new leaves on the trees. Sometimes it rains but the air is fresh. Spring is a good time to start new things. I like it more than summer because it is not too hot.

---

## Advanced — Anchor 1 (Score: 13/16)

Grammar 3, Lexis 4, Organization 3, Content 3

I prefer winter to other seasons. The cold weather and short days give me a chance to stay indoors and read or watch films. I also like the quiet atmosphere after snowfall. Every year my family and I visit a nearby mountain to ski. Although the season can be harsh, I find it refreshing and it helps me appreciate the warmth of spring when it arrives.

---

## Advanced — Anchor 2 (Score: 14/16)

Grammar 4, Lexis 4, Organization 4, Content 2

Autumn is my favorite season. The temperature is mild and the scenery is beautiful as the leaves turn red and yellow. I often take long walks and take photographs. The season also reminds me of the start of the school year and new goals. For me, autumn is the best time to reflect and prepare for the rest of the year.

---

## CSEE replacement guide

To use essays from the CSEE dataset (Xiaochr/Chinese-Student-English-Essay on HuggingFace):

1. Filter by score band or prompt type; pick 4–6 essays per level (Basic / Intermediate / Advanced).
2. Assign rubric scores (Grammar, Lexis, Organization, Content) to each selected essay.
3. Replace the anchor blocks above with the CSEE essay text and your assigned scores.
4. Keep the same markdown structure (level, anchor number, score line, then essay body) so the agent can parse it.
