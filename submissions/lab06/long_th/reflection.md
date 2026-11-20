# Lab 6 — H2 reflection (long_th)

Explain RAG to a friend who never studied AI, using the picture of an open-book exam. Mention at least one
thing **our code** checks that the model does not (e.g. the grounding check, or the `min_score` threshold).
Exactly 5 lines between the markers, in your own words (English or Vietnamese). Do not copy a teammate.

<!-- reflection:start -->
RAG is like an open-book exam: instead of answering from memory, the assistant first finds the right page of the student handbook and then writes its answer from that page.
Finding the page is a search: the handbook is cut into small sections and each one is scored by how well it matches the question's words (BM25), like flipping to the chapter whose heading fits.
If no section scores at least `min_score` (2.0), our code stops before the model is even asked and sends the student to the Training Office — a good student writes "not in the book" instead of guessing.
When the model does answer it must name the pages it used, and our grounding check throws the answer away if it cites a page we never gave it; the model cannot check that about itself, so the code does.
An open book only helps if you open it at the right page: in my tests the word "fee" sent a student-card question to the tuition calculator and "another student's grades" slipped past the privacy guard.
<!-- reflection:end -->
