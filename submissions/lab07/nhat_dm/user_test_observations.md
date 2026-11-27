# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Minh  Date: 2026-11-27
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Typed both parts of the task into one message ("Can I register my thesis with 118 credits, and where to replace a lost student card?") instead of asking separately. | Expected a clear two-part answer covering both the thesis credit requirement and the lost card office/process. | The chat input (`st.chat_input`) accepts free-form multi-question prompts without hinting that single-topic queries retrieve better sources. | Add a short hint in the welcome message or input placeholder recommending one question at a time, or split multi-part queries in the backend. |
| 2 | | | | |
| 3 | | | | |

The one change we made (commit link):
Before / after screenshot:
