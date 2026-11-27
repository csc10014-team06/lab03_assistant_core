# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Khoi  Date: 2026-11-27

Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Asked what documents he needed to bring to replace a lost student card. | A list of required documents to avoid an unnecessary trip. | The assistant returned the replacement location instead of explaining which documents were required. | Provide a checklist of required documents when available, or direct the user to Student Affairs to confirm the requirements. |
| 2 | Asked how much it costs to replace a lost student card. | A specific fee amount so he could prepare enough money. | The assistant returned the replacement location instead of the requested fee and did not acknowledge that the fee information was missing from its answer. | Clearly state when the requested information is unavailable and direct the user to Student Affairs to confirm the fee. |
| 3 | Could not determine where to find the original documents cited by the assistant. | Direct access to the original sources to verify the answers. | Sources displayed document identifiers and section titles without clickable links. | Add clickable links to the original documents when available. |

The one change we made (commit link): Pending team UI fix.
Before / after screenshot: Pending implementation.
