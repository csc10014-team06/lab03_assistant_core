# Lab 6 — H2 reflection (truyen_lp)

Explain RAG to a friend who never studied AI, using the picture of an open-book exam. Mention at least one
thing **our code** checks that the model does not (e.g. the grounding check, or the `min_score` threshold).
Exactly 5 lines between the markers, in your own words (English or Vietnamese). Do not copy a teammate.

<!-- reflection:start -->
Think of an AI chatbot like a clever student taking an exam: normally it answers from memory (closed-book), which makes it guess or invent rules it never read.
RAG turns that into an open-book exam by first using our search code to find the exact handbook paragraph and handing only that page to the model.
The model's job is just to phrase a friendly answer from that paragraph rather than making up policies, fees, or deadlines on its own.
Even then, we never trust the model blindly: our code runs a `min_score` threshold before calling the model so irrelevant questions abstain immediately.
Our code also runs a grounding check after the model replies to reject any answer that fails to cite a retrieved source ID or cites a made-up one.
<!-- reflection:end -->
