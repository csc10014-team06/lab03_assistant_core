# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Anh  Date: 2026-11-27
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Asked both questions in a single long message ("Can I register thesis with 118 credits and where to replace lost student card?") | Expected a combined answer covering both thesis eligibility and student card replacement | The retriever matched only one top topic (`H26#5.3`) and ignored the second question in the compound prompt | Add a short tip in the welcome message advising users to ask one question at a time |
| 2 | Looked at the `Sources: H26#5.3 - Thesis registration` line and tried clicking on it | Expected a clickable link or expandable popup showing the exact policy excerpt | `format_sources` renders plain text strings rather than an interactive expander | Wrap source snippets inside `st.expander("View source text")` under the answer |
| 3 | Clicked the 👍 button after reading the first answer and looked around to see if it saved | Expected the button to stay highlighted in green rather than disappearing completely | Adding `request_id` to `st.session_state.rated` hides both rating buttons immediately after voting | Replace the hidden buttons with a persistent static badge like `"Feedback recorded"` |

The one change we made (commit link):
Before / after screenshot: