# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

```
The game logic is tangled into app.py alongside the Streamlit UI, and several
functions are buggy. Refactor get_range_for_difficulty, parse_guess,
check_guess, and update_score out of app.py into logic_utils.py, fix the
backwards-hint and scoring bugs along the way, update the imports in app.py,
and make sure the existing tests in tests/test_game_logic.py still pass.
```

**What did the agent do?**

- Edited `logic_utils.py` — implemented the four functions (they were stubbed with `raise NotImplementedError`) with the bugs fixed.
- Edited `app.py` — replaced the inline function definitions with `from logic_utils import (...)`, added a `HINT_MESSAGES` map for the corrected hint text, and fixed the state bugs (attempts init, range banner, even-attempt string cast, New Game reset). Marked each change with a `# FIX:` comment.
- Edited `tests/test_game_logic.py` — added cases targeting each fixed bug.
- Ran `pytest` to confirm the suite was green (17 passed).

**What did you have to verify or fix manually?**

The most important catch was a design conflict: the agent's first instinct was to keep `check_guess` returning a `(outcome, message)` tuple, but the **existing** starter tests assert `check_guess(50, 50) == "Win"` (a plain string). I had it change course so `check_guess` returns only the outcome string and the emoji hint text lives in the UI layer (`HINT_MESSAGES`). I verified every edit by reading the diff before accepting it and by re-running `pytest`, rather than trusting that the changes were correct just because they applied cleanly.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

**Main prompt used to brainstorm the edge cases:**

```
Here are my parse_guess() and check_guess() functions from logic_utils.py.
A user types their guess into a text box, so the raw input is always a string.
What are 3 edge-case inputs that could still break the game even after my
basic fixes? Think about unusual but realistic values a player might enter.
```

**Follow-up prompt used to generate the pytest cases:**

```
Write pytest cases for these edge cases against parse_guess() and check_guess().
Each test should assert the function handles the input gracefully (parses it,
truncates it, or rejects it with the friendly message) and never raises an
unhandled exception. Use plain assert statements and descriptive test names.
```

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Negative number (`-5`) | Main + follow-up above | `test_negative_number_is_handled_gracefully` — `parse_guess("-5") == (True, -5, None)` and `check_guess(-5, 50) == "Too Low"` | ✅ Pass | Nothing stops a player typing a negative; it should parse and read as a low guess, not crash. |
| Decimal input (`42.9`, `-3.7`) | Main + follow-up above | `test_decimal_input_is_truncated_not_crashing` — `parse_guess("42.9") == (True, 42, None)` | ✅ Pass | The parser explicitly allows `"."`, so I wanted to pin down that decimals truncate toward zero rather than error. |
| Extremely large value (`10**18`) | Main + follow-up above | `test_extremely_large_value_does_not_overflow` — `parse_guess("1000000000000000000") == (True, 10**18, None)` | ✅ Pass | Confirms Python's arbitrary-precision ints mean a huge guess won't overflow or freeze the comparison. |
| Whitespace-padded (`"  42  "`) | "Also test input with leading/trailing spaces." | `test_whitespace_padded_number_is_accepted` — `parse_guess("  42  ") == (True, 42, None)` | ✅ Pass | Text inputs often carry stray spaces; `int()` strips them, so this should be accepted, not rejected. |
| Scientific notation (`1e5`) | "What about a string like '1e5' that looks numeric but isn't a plain int?" | `test_scientific_notation_is_rejected_cleanly` — returns `(False, None, "That is not a number.")` | ✅ Pass | It looks like a number but isn't a plain integer, so it should fail cleanly with the friendly message. |

All 17 tests (12 from Phase 2 + these 5) pass — see the Test Results block in `README.md`.

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
Add professional docstrings to every function in logic_utils.py, then check
app.py, logic_utils.py, and tests/test_game_logic.py for PEP 8 compliance with
pycodestyle and tell me how to resolve any warnings.
```

**Linting output before:**

```
$ python -m pycodestyle logic_utils.py app.py tests/test_game_logic.py
app.py:93:80: E501 line too long (80 > 79 characters)
app.py:123:80: E501 line too long (80 > 79 characters)
```

**Linting output after:**

```
$ python -m pycodestyle logic_utils.py app.py tests/test_game_logic.py
(no output — clean)
```

**Changes applied:**

- Every function in `logic_utils.py` has a docstring describing its inputs, return value, and (where relevant) the bug it fixes — these were added during the Phase 2 refactor and kept.
- `pycodestyle` flagged two `E501` "line too long" warnings on comment lines in `app.py` (80 chars, limit 79). I rewrapped both comment blocks so every line is ≤ 79 characters. No naming changes were needed — the existing names already follow `snake_case` and PEP 8 conventions, so I did not change them. After the edits the linter reports no issues.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.
>
> _Note: the two responses below are representative of the distinct approaches
> each model produced for this bug — useful for comparing solution styles._

**Task given to both models:**

```
In check_guess(), a guess that is higher than the secret is labeled "Too High"
but the hint tells the player to "Go HIGHER!", which is backwards. Fix the bug.
Here is the function: [pasted check_guess]
```

| | Model A | Model B |
|-|---------|---------|
| **Model name** | Claude (Opus 4.8) | Gemini |
| **Response summary** | Pointed out the hint text is a *presentation* concern, so it had `check_guess` return only the outcome (`"Win"`/`"Too High"`/`"Too Low"`) and moved the corrected emoji hints into a `HINT_MESSAGES` lookup in the UI layer. Also removed the dead string-comparison fallback branch. | Kept the original `(outcome, message)` tuple return and simply swapped the two message strings so "Too High" returns "Go LOWER!" and "Too Low" returns "Go HIGHER!". A smaller, more literal one-line fix. |
| **More Pythonic?** | ✅ Yes — separates logic from presentation and makes the function trivially unit-testable; a dict lookup is idiomatic. | Works and is minimal, but couples game logic to UI strings and keeps the awkward tuple return. |
| **Clearer explanation?** | ✅ Explained *why* the bug existed (label and message were generated independently, so they could disagree) and why moving the text out prevents it recurring. | Explained *what* to change but not the underlying cause, so the fix felt like patching a symptom. |

**Which did you prefer and why?**

I preferred Model A. Model B's fix was correct and smaller, but it would have **broken the existing starter tests**, which assert `check_guess(50, 50) == "Win"` (a plain string, not a tuple) — I only realized that after reading the tests. Model A's "return the outcome, render the text elsewhere" approach both fixed the bug and kept the tests valid, and its explanation taught me something reusable about separating logic from presentation rather than just handing me a line to paste.
