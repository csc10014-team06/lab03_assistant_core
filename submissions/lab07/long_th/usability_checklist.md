# Lab 7 — Usability checklist (tick before your user test)

- [x] The first screen says what the assistant can do, with example questions — welcome message with one example in the chat; 4 example buttons in the sidebar
- [x] Empty or too-long input shows a friendly message (not a crash) — 2001 characters → "Your question is too long (max 2000 characters)."; an empty message cannot be sent (send button disabled)
- [x] While waiting, the user sees "Thinking…" — seen with a backend that takes 3 s; with the offline stub the answer is too fast to notice
- [x] Every answer from documents shows its sources — "Sources: S26#3 — 3 Student card replacement" under the answer
- [x] "I don't know" answers tell the user who can help (escalation) — "what is the capital of France" → note pointing to the Training Office, room I.101
- [x] If the backend is down, the page says so clearly — red banner "The assistant backend is not reachable…" and "Cannot reach the assistant. Is the backend running?" on send
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message — 👎 → toast "Thanks — we will look at this answer." and a rating −1 row is stored
- [ ] The page says it is an AI assistant — only in the sidebar; on a phone (375 px wide) the sidebar starts collapsed, so the first screen never says it is an AI (examples are hidden too)
- [ ] Text is readable (size, contrast); buttons have clear labels — answers are fine (16 px, 12.5:1), but the grey "Sources:" caption is 14 px at about 3.7:1 contrast (below the 4.5:1 WCAG AA minimum), and 👍 / 👎 are emoji-only buttons with no text label
- [x] Works on a phone-width window — at 375 px: no sideways scrolling, chat, sources and 👍 / 👎 work (buttons stack vertically); see the note on the AI notice above
