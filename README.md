# Study Assistant Core (`assistant_core`)

A modular, robust, and tested Python package refactored from a legacy study assistant monolith. It answers student queries regarding university offices, tuition fees, and student handbook regulations.

---

## Architecture & Features

The monolithic codebase (`monolith/assistant_monolith.py`) was decomposed into cohesive, single-responsibility modules:

- **`config.py`**: Immutable dataclass configuration (`Settings`) loaded from environment variables (`ASSISTANT_*`), securing secrets and replacing magic numbers.
- **`data_loader.py`**: Robust data parsing for `offices.csv` and `handbook.json` with strict error handling (`DataLoadError`), safe resource management (`with` statements), and dataclasses (`Office`, `Rule`).
- **`fees.py`**: Pure functions for fee queries parsing (`parse_fee_query`) and tuition calculation (`compute_tuition`), handling retake multipliers and credit limits.
- **`offices.py`**: Pure office lookup and fuzzy keyword matching.
- **`handbook.py`**: Handbook rule retrieval based on token overlap and keyword scoring, including an AI-extended feature for exam absence deadlines.
- **`llm.py`**: Decoupled LLM client protocol (`LLMClient`) with deterministic `FakeLLM` for testing and `DemoLLM` for demonstration.
- **`service.py`**: Central coordinator (`AssistantService`) orchestrating intent routing, query history, session statistics, and secure history export without path traversal.
- **`cli.py`**: CLI entry point supporting both one-shot queries and interactive REPL mode with configurable structured logging.

---

## Requirements

- Python 3.10 or higher

---

## Installation

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd lab03_assistant_core
   ```

2. **Create and activate a virtual environment:**
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

3. **Install the package and dependencies:**
   ```bash
   pip install -e .
   ```
   Or install development dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Configuration settings are read through `assistant_core.config.load_settings()`. You can customize settings via environment variables or a `.env` file.

Copy the example file:
```bash
cp .env.example .env
```

Available environment variables:
| Variable | Default | Description |
|---|---|---|
| `ASSISTANT_API_KEY` | `None` | API key for LLM services (never hard-coded or logged) |
| `ASSISTANT_MODEL` | `gpt-small` | Model name |
| `ASSISTANT_DEBUG` | `false` | Enable verbose debug logging |
| `ASSISTANT_CREDIT_RATE` | `450000` | Tuition rate per credit (VND) |
| `ASSISTANT_RETAKE_MULTIPLIER` | `1.5` | Multiplier for retake credits |
| `ASSISTANT_MAX_CREDITS` | `30` | Maximum allowed credits per semester |
| `ASSISTANT_DATA_DIR` | `assistant_core/data` | Path to office and handbook data |
| `ASSISTANT_HISTORY_DIR` | Current working directory | Directory to save session logs |

---

## Usage

You can use the assistant via the command line with either `assistant` (after `pip install -e .`) or `python -m assistant_core`.

### 1. One-Shot Mode
Provide your question as an argument to get an immediate answer:
```bash
python -m assistant_core "where is the library"
# Output: Library: room B.201, open Mon-Sat 07:00-20:00

python -m assistant_core "tuition 18 credits 2 retakes"
# Output: Your tuition is 9450000 VND (18 credits, 2 retakes)
```

### 2. Interactive REPL Mode
Run without arguments to enter an interactive conversation loop:
```bash
python -m assistant_core
```
```text
============================================================
Study Assistant Core
Ask me questions about:
  * Offices:   e.g. 'where is the library?', 'health service'
  * Tuition:   e.g. 'tuition 18 credits 2 retakes', 'fees'
  * Handbook:  e.g. 'exam absence', 'thesis rule', 'max credits'
  * Commands:  'stats', 'save <filename>', 'quit'
Type 'quit' or 'exit' to exit.
============================================================
> where is the medical room?
Health Service: room A.105, open Mon-Fri 08:00-16:30
> stats
fee=0 office=1 rule=0 other=0
> quit
Goodbye!
```

### 3. Debug Logging
Enable verbose debug logs via the `--debug` flag:
```bash
python -m assistant_core "hi" --debug
```

---

## Testing & Code Quality

The test suite includes characterization tests verifying backwards compatibility against the legacy monolith, as well as comprehensive unit tests for each module.

- **Run all tests:**
  ```bash
  pytest
  ```
- **Run tests with verbose output and coverage:**
  ```bash
  pytest -v
  ```
- **Run linter and code formatting check:**
  ```bash
  ruff check .
  ```