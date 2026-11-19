# Lab 6 — Team baseline: rules vs retrieval vs llm

Generated on `main` with `python eval/compare_paths.py` (offline, stub provider). Re-generate after every merge
that touches `assistant_core/rag/`, `assistant_core/data/kb/` or `eval/cases.jsonl`; with every member's H1
cases: `python eval/compare_paths.py --include-submissions`.

Cases: 20 · `RETRIEVAL_MIN_SCORE=2.0` · k=3 · provider: `stub`

| path | passed | accuracy | right source (normal) | abstained correctly | false abstain | wrong source | grounding rejected | mean latency (ms) | failed |
|---|---|---|---|---|---|---|---|---|---|
| rules | 9/20 | 45% | 5/15 | 4/5 | 7 | 3 | 0 | 0.05 | E01, E02, E03, E04, E05, E06, E07, E08, E13, E15, E19 |
| retrieval | 16/20 | 80% | 12/15 | 4/5 | 2 | 1 | 0 | 0.02 | E13, E14, E15, E19 |
| llm (stub) | 16/20 | 80% | 12/15 | 4/5 | 2 | 1 | 0 | 0.02 | E13, E14, E15, E19 |

<details><summary>Per-case results</summary>

| id | category | question | expected | rules | retrieval | llm |
|---|---|---|---|---|---|---|
| E01 | normal | how many books can I borrow at once | S26#1 | ❌ abstain | ✅ S26#1 | ✅ S26#1 |
| E02 | normal | I lost my student card | S26#3 | ❌ H26#1 | ✅ S26#3 | ✅ S26#3 |
| E03 | normal | what is the fine for overdue books | S26#2 | ❌ abstain | ✅ S26#2 | ✅ S26#2 |
| E04 | normal | I forgot my email password | S26#4 | ❌ abstain | ✅ S26#4 | ✅ S26#4 |
| E05 | normal | how do I connect to the campus wifi | S26#5 | ❌ abstain | ✅ S26#5 | ✅ S26#5 |
| E06 | normal | what GPA do I need for a merit scholarship | S26#6 | ❌ abstain | ✅ S26#6 | ✅ S26#6 |
| E07 | normal | when can I apply for the dormitory | S26#7 | ❌ H26#2 | ✅ S26#7 | ✅ S26#7 |
| E08 | normal | is health insurance mandatory | S26#8 | ❌ abstain | ✅ S26#8 | ✅ S26#8 |
| E09 | normal | how much does it cost to retake a course | H26#1 | ✅ H26#1 | ✅ H26#1 | ✅ H26#1 |
| E10 | normal | how many credits do I need to register a thesis | H26#2 | ✅ H26#2 | ✅ H26#2 | ✅ H26#2 |
| E11 | normal | what is the maximum credit load per semester | H26#4 | ✅ H26#4 | ✅ H26#4 | ✅ H26#4 |
| E12 | normal | I missed the final exam because I was sick | H26#5 | ✅ H26#5 | ✅ H26#5 | ✅ H26#5 |
| E13 | synonym | can I get my money back if I drop a class | H26#8 | ❌ abstain | ❌ abstain | ❌ abstain |
| E14 | plural | what are the deadlines for retakes | H26#1 | ✅ H26#1 | ❌ abstain | ❌ abstain |
| E15 | wrong-chunk | who at the Training Office can fix a wrong exam grade | H26#6 | ❌ (no source) | ❌ H26#5 | ❌ H26#5 |
| E16 | out-of-scope | what is the capital of France | abstain | ✅ abstain | ✅ abstain | ✅ abstain |
| E17 | out-of-scope | who will win the football match tonight | abstain | ✅ abstain | ✅ abstain | ✅ abstain |
| E18 | out-of-scope | what is the weather like tomorrow | abstain | ✅ abstain | ✅ abstain | ✅ abstain |
| E19 | other-person | did my classmate Minh get a merit scholarship this semester | abstain | ❌ H26#4 | ❌ S26#6 | ❌ S26#6 |
| E20 | out-of-scope | write me a poem about the moon | abstain | ✅ abstain | ✅ abstain | ✅ abstain |

</details>

## What the columns mean

| column | meaning |
|---|---|
| passed / accuracy | cases where the path did the right thing (cited the expected chunk, or abstained when it should) |
| right source (normal) | of the questions that *should* be answered, how many cited the expected chunk |
| abstained correctly | of the questions that should get "I don't know", how many did |
| false abstain | answerable questions where the path said "I don't know" (A1 threshold too strict / vocabulary gap) |
| wrong source | answered, but from the wrong chunk (the dangerous kind of error) |
| grounding rejected | drafts thrown away by the A2 check because they cited a chunk we never retrieved |

## Why the four expected failures fail (retrieval and llm)

| case | category | what happens | possible fix |
|---|---|---|---|
| E13 | synonym | "money back / drop a class" shares no word with "refund / withdraw" → score 0 → abstain | synonyms or embeddings |
| E14 | plural | "deadlines / retakes" ≠ "deadline / retake" → score 0 → abstain | stemming (bonus H3 makes it pass: 17/20) |
| E15 | wrong-chunk | "Training Office" + "exam" match the exam-absence chunk better than the grade-review chunk | weight rare words (TF-IDF / BM25) |
| E19 | other-person | "merit scholarship semester" scores 3, the stub always answers; nothing checks *whose* data is asked | a person/privacy check before retrieval, or a real model that abstains |

The rules path also answers *"I lost my student card"* with the **retake** rule (keyword "student" + "lost" inside
"students"), and E15 with the Training Office's opening hours — keyword rules cannot say "I don't know" reliably.
