# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Minh  Date: 2026-11-27
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Typed both parts of the task into one message ("Can I register my thesis with 118 credits, and where to replace a lost student card?") instead of asking separately. | Expected a clear two-part answer covering both the thesis credit requirement and the lost card office/process. | The chat input (`st.chat_input`) accepts free-form multi-question prompts without hinting that single-topic queries retrieve better sources. | Add a short hint in the welcome message or input placeholder recommending one question at a time, or split multi-part queries in the backend. |
| 2 | Ignored the "Try an example" buttons in the sidebar and typed the entire thesis question manually; only noticed the "I lost my student card" button afterward. | Expected example prompts to be visible inside the main chat area (e.g., right below the welcome message). | Example buttons are placed in `st.sidebar`, away from the user's primary focus at the center/bottom of the chat window. | Display quick-reply example chips directly below the `WELCOME` message in the main chat container. |
| 3 | Hovered and clicked on the `Sources: ...` caption line below the assistant's reply, then asked "Can I open the handbook section from here?" | Expected the source citation to be clickable or expandable so they could verify the exact rule. | `st.caption(m["sources"])` renders plain text with no `st.expander` or link to the source excerpt. | Render sources inside an `st.expander("Sources")` showing the document ID, title, and a short excerpt. |
| 4 | Clicked the 👍 button, saw the buttons disappear immediately, and wondered if the feedback was actually recorded. | Expected a persistent "Thanks for your feedback" indicator next to the message instead of the buttons vanishing. | `st.session_state.rated.add(rid)` hides both buttons on rerun, and `st.toast` disappears quickly at the corner of the screen. | Replace the 👍/👎 buttons with a small static label like `Feedback recorded (👍)` after the user votes. |

The one change we made (commit link):
Before / after screenshot:
