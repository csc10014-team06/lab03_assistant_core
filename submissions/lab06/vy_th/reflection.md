# Lab 6 — H2 reflection (vy_th)

Explain RAG to a friend who never studied AI, using the picture of an open-book exam. Mention at least one
thing **our code** checks that the model does not (e.g. the grounding check, or the `min_score` threshold).
Exactly 5 lines between the markers, in your own words (English or Vietnamese). Do not copy a teammate.

Imagine I am taking an exam where I can look up information in my textbooks.
Instead of trying to remember everything, I find the section related to the question.
RAG works similarly by giving AI relevant documents before asking it to answer.
In this lab, I learned that our code checks whether the sources cited by AI were actually retrieved.
I also realized that finding a related document does not always mean it contains the correct answer, as shown in case E19.
