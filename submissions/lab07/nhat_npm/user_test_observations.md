# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Ha  Date: 27/11/2026
Task they tried: “Find out if you can register your thesis with 118 credits, and where to replace a lost student card.” The tester also entered “abc” and selected the “I lost my student card” example.

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Asked the credits question. | Expected the credits question to be handled; the tester said the result matched their expectation. | No confusion or unexpected behavior was reported during this step. | No change suggested from this observation. |
| 2 | Entered “abc” and saw the assistant say it could not answer from the official documents and direct them to the Training Office. | The tester did not expect the escalation. For unclear or out-of-scope input, abstaining and directing the user to staff is the intended behavior. | The assistant correctly could not find an answer in the official documents and displayed the escalation path. | No change; keep the abstention and Training Office guidance for unsupported questions. |
| 3 | Clicked the “I lost my student card” example. | Expected the example question to be submitted; the tester said it behaved as expected. | The example button let the tester choose the student-card question; no confusion was reported. | No change suggested from this observation. |

The one change we made (commit link): No UI fix was identified by this test.
Before / after screenshot: Not taken; no change was made.
