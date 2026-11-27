# Lab 7 — Usability checklist (tick before your user test)

- [x] The first screen says what the assistant can do, with example questions
- [x] Empty or too-long input shows a friendly message (not a crash)
- [ ] While waiting, the user sees "Thinking…" — with the local offline stub backend, replies return in under 1 second so the spinner was not visible in practice
- [x] Every answer from documents shows its sources
- [x] "I don't know" answers tell the user who can help (escalation)
- [x] If the backend is down, the page says so clearly
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message
- [ ] The page says it is an AI assistant — shown in the sidebar caption on desktop, but hidden on a 375 px phone window because the sidebar starts collapsed
- [ ] Text is readable (size, contrast); buttons have clear labels — main text is readable, but the Sources caption is smaller muted grey text and 👍 / 👎 buttons are emoji-only without text labels or aria-labels
- [x] Works on a phone-width window
