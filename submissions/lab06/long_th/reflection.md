# Lab 6 — H2 reflection (long_th)

Explain RAG to a friend who never studied AI, using the picture of an open-book exam. Mention at least one
thing **our code** checks that the model does not (e.g. the grounding check, or the `min_score` threshold).
Exactly 5 lines between the markers, in your own words (English or Vietnamese). Do not copy a teammate.

<!-- reflection:start -->
Think of our assistant as a student in an open-book exam: it is not allowed to answer from memory, so it first looks up the right page in the student handbook and only then writes the answer from that page.
To find the page it does what you would do with the index at the back of a book: the handbook is cut into short sections, and each section gets a score for how many of the question's words it contains.
If even the best page scores below `min_score` (2.0), our code stops right there, never asks the model, and tells the student to ask the Training Office, like a good student who writes "this is not in the book" instead of making something up.
When the model does answer, it has to write down which pages it used, and our grounding check throws the answer away if it names a page we never gave it; the model cannot catch its own invented citations, so our code checks them.
The open book only helps if you open it at the right page: in my tests the word "fee" sent a lost-card question to the tuition calculator, and "another student's grades" got past the privacy check, so the searching and the checks matter as much as the model.
<!-- reflection:end -->
