# Lab 6 — H2 reflection (nhat_npm)

Explain RAG to a friend who never studied AI, using the picture of an open-book exam. Mention at least one
thing **our code** checks that the model does not (e.g. the grounding check, or the `min_score` threshold).
Exactly 5 lines between the markers, in your own words (English or Vietnamese). Do not copy a teammate.

<!-- reflection:start -->
Imagine you have a very smart friend who can explain anything beautifully, but sometimes makes things up when they don't actually know the answer.
RAG is like giving that friend an open-book exam: instead of letting them answer from memory, we first search our own documents to find the right page, then hand it to them and say "answer only from this page."
If the search finds nothing relevant (the score is below our min_score threshold), we don't even ask the friend — we just say "I don't know," which is safer and cheaper than risking a made-up answer.
Even when the friend does answer, our code runs a grounding check: it verifies that every source the friend cites is one we actually gave them, catching any invented references.
The model itself has no such self-check — it cannot tell whether it is citing real sources or hallucinating, so our code acts as the safety net.
<!-- reflection:end -->
