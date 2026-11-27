# Lab 6 — H2 reflection (han_htg)

Explain RAG to a friend who never studied AI, using the picture of an open-book exam. Mention at least one
thing **our code** checks that the model does not (e.g. the grounding check, or the `min_score` threshold).
Exactly 5 lines between the markers, in your own words (English or Vietnamese). Do not copy a teammate.

<!-- reflection:start -->
Answering policy questions with RAG works like an open-book exam where you can only cite from the pages placed on your desk.
First, the retriever searches for matching pages, and our code checks `min_score` (A1) to abstain instead of guessing when no page is relevant enough.
Next, the LLM drafts a response using only those retrieved chunks rather than relying on its pre-trained memory.
However, a model can still hallucinate or invent a citation ID that was never handed to it in the prompt.
Our deterministic grounding check in `parse_draft` (A2) verifies that every cited `source_id` actually belongs to the retrieved chunks—something the model itself cannot guarantee.
<!-- reflection:end -->
