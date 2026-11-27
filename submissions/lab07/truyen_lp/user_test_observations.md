# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Quyen  Date: 2026-11-28
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Asked both parts of the task in one natural question ("can I register my thesis if I currently have 118 credits? Also, where do I go to replace a lost student card?"). | Both parts answered, or a clear notice that only one question can be handled at a time. | Single-intent routing answered only the student card clause (`Student Affairs, room I.102`) and silently dropped the thesis question. | Split/detect multi-question prompts and answer each part, or explicitly tell the user which part was skipped. |
| 2 | Asked follow-ups without repeating keywords ("Can I get an exception with 118 credits?" and "What documents or fee are needed to replace a lost student card?"). | Answers tied to the active topic (thesis exception; student card documents/cost). | Stateless keyword routing hijacked `"credits"` to `2 Retake fee` and `"fee"` to `"How many credits?"` (tuition calculator). | Pass recent conversation topic into routing and require tuition context before entering the `"How many credits?"` prompt. |
| 3 | Asked "Can I register my thesis with 118 credits?" and later "What documents do I need to bring... and how much does it cost?". | A direct "No (2 credits short of 120)" for thesis, and an honest note when card fee/documents are not in the handbook. | Responses literally quoted a single matched sentence (`5.3 Thesis registration` / `3 Student card replacement`) without comparing numbers or stating missing details. | State a direct Yes/No when comparing user numbers to rules, and explicitly say when requested details are absent (pointing to Student Affairs I.102 / Training Office I.101). |
| 4 | Tried to open/verify `Sources: S26#3 — 3 Student card replacement` and checked office answers (`Training Office`, `Student Affairs`). | Clickable links or expandable excerpts to read the official document, and citations on office answers too. | `Sources:` is rendered as plain caption text with internal IDs (`S26#3`, `H26#5.3`) and zero links, while office replies omit sources. | Add an `st.expander("View source excerpt")` (and official link if available) and show the office directory source on office answers. |
| 5 | Clicked thumbs down and thumbs up, looked for a way to reset the chat, and submitted with Enter. | Persistent rated badge (plus optional reason on thumbs down), a "New chat" button, and clean input reset on Enter. | Feedback buttons disappeared on the next turn with no saved-state indicator, no "New chat" button exists, and pressing Enter left a trailing newline hiding the placeholder. | Keep a disabled/selected feedback indicator (e.g. `st.feedback`), add a sidebar "New chat" button, and clear trailing newlines after Enter. |

The one change we made (commit link): Pending team UI fix.
Before / after screenshot: Pending implementation.
