# Lab 6 — T7 bonus (han_htg) — optional, pick one

<!-- Delete the option you did not do and replace every TODO. Leave this file untouched if you skip the bonus. -->

## Option Ollama
`cd lab06/starter && LLM_PROVIDER=ollama LLM_MODEL=llama3.2 python eval/compare_paths.py`
(needs `ollama serve` + `ollama pull llama3.2`)

- Slower than the stub? (p50 / max ms): TODO
- Did E19 become "I don't know"? TODO
- Did any case get worse? Which and why: TODO

## Option H3
Change `tokenize` in `lab06/starter/src/assistant_core/rag/index.py` to strip a trailing `s` from words longer than
4 letters (on your branch only — the team merges one version).

- Does E14 pass now? TODO
- What else changed in the table? TODO
