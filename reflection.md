# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran it, the game *looked* fine — it loaded, took guesses, kept a score, and even had a "Developer Debug Info" panel that showed the secret number. But playing it a couple of times, the feedback made no sense. None of the bugs actually crash the app or print an error to the console; they're all silent **logic** bugs, which made them harder to trust at first.

Concrete bugs I noticed:

- **The hints are backwards.** When my guess was higher than the secret, it labeled it "Too High" but the message told me to "Go HIGHER!" — the exact wrong direction.
- **Every other guess gives nonsense hints.** On even-numbered attempts the code turns the secret into text and compares it as a string, so a guess of `100` was reported as "Too Low" against a secret of `20` (because the text `"100"` sorts before `"20"`).
- **The score goes up when I guess wrong.** A "Too High" guess on an even attempt *adds* 5 points instead of penalizing me, so the score drifts in the wrong direction.
- **Winning fast is punished.** Guessing correctly on the very first try only awarded 70 points instead of the expected ~90–100, because the scoring formula counts one extra attempt.
- **UI counters lie.** "Attempts left" starts one too low (the attempt counter is initialized to `1`), and the banner always says "between 1 and 100" even on Easy (range 1–20) or Hard (range 1–50).
- **New Game doesn't fully reset.** It doesn't clear the score or the won/lost status, so after a game ends the board stays stuck on "Game over / You already won."

**Bug Reproduction Log**

> All reproductions use the **Developer Debug Info** expander to read the current secret, so each case is deterministic. Difficulty = Normal unless noted.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Secret = 30, guess `60` (odd attempt #1) | Hint: "Too High → go lower" | Label "Too High" but message says **"📈 Go HIGHER!"** | none |
| Secret = 20, guess `100` on the **2nd** (even) attempt | Hint: "Too High → go lower" | Reported as **"Too Low / 📉 Go LOWER!"** (100 treated as smaller than 20) | none |
| Any wrong guess of "Too High" on an even attempt (e.g. attempt #2), starting score 0 | Score drops by 5 (or stays) | Score **increases to 5** for a wrong guess | none |
| Win on the **first** guess (secret matches your first input) | ~90–100 points awarded | Only **70 points** awarded | none |
| Difficulty = **Easy**, before guessing | Banner: "between 1 and 20", "Attempts left: 6" | Banner says **"between 1 and 100"**, **"Attempts left: 5"** | none |
| After losing, click **New Game 🔁** | Fresh game: score 0, can play again | Score persists and board stays on **"Game over"** | none |

---

## 2. How did you use AI as a teammate?

I used my AI coding assistant in VS Code (Claude Code) as a pair programmer. I attached `app.py` and `logic_utils.py` so it could see how the UI and logic files related to each other, then worked one bug at a time.

**A correct suggestion:** The AI suggested refactoring the four game functions out of `app.py` into `logic_utils.py`, and — importantly — making `check_guess` return *only* the outcome string (`"Win"`/`"Too High"`/`"Too Low"`) while keeping the emoji hint text in the UI layer. This kept the logic presentation-free and meant the existing starter tests (which expect `check_guess(50, 50) == "Win"`) still passed. I verified this by running `pytest`: all 12 tests passed, including the 3 original ones.

**A misleading suggestion:** Early on, the AI's first read of the code claimed "you can't win on even-numbered attempts" because the secret gets cast to a string. That sounded plausible, but when we actually *ran* the function, `check_guess(30, "30")` still returned `"Win"` — the buggy string-comparison fallback happened to match. So the real bug wasn't "can't win," it was "hints become nonsense" (e.g. `check_guess(100, "20")` reports "Too Low"). I caught the overstatement by running the code instead of trusting the explanation, which is the whole lesson: verify, don't assume.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed only when I could (a) write a test that *failed* on the old behavior and *passed* on the new code, and (b) see the correct behavior in the live Streamlit game using the Developer Debug Info panel to read the secret.

The clearest test was for the even-attempt comparison bug: `assert check_guess(100, 20) == "Too High"`. Under the old string-comparison code, `"100"` sorted before `"20"`, so it returned "Too Low"; after the fix (comparing as integers) it correctly returns "Too High". I also added `assert update_score(0, "Too High", 2) == -5` to prove a wrong guess no longer secretly *adds* points, and `assert update_score(0, "Win", 1) == 100` to prove a first-guess win gives full points instead of 70. Running `pytest` showed **12 passed**.

AI helped me design the tests by suggesting the "test the bug, not just the happy path" idea — pick the exact input that used to break (guess 100 vs secret 20) and assert the corrected result, so the test would have caught the original glitch.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Streamlit re-runs your entire script from top to bottom every time the user interacts with the page — clicking a button, typing in a box, anything. So any normal variable you create is born fresh and forgotten on every click, like the script has amnesia. `st.session_state` is the app's long-term memory: values you store there (like the secret number, the score, and the attempt count in this game) survive across reruns. That's why the code carefully checks `if "secret" not in st.session_state` before generating one — so the secret is picked once and remembered, instead of being re-rolled on every guess. Understanding this was key to seeing why "New Game" had to explicitly reset each stored value rather than just hoping they'd clear themselves.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

The biggest habit I want to keep is **writing a test that reproduces the bug before I trust the fix**. For each glitch I picked the exact input that used to break (like guess 100 vs secret 20) and asserted the correct result, so the test would have failed on the old code. That turned "I think it's fixed" into "pytest proves it's fixed." I also want to keep the habit of separating logic from UI — moving the rules into `logic_utils.py` made everything testable.

- What is one thing you would do differently next time you work with AI on a coding task?

I'd verify the AI's *explanations* as critically as its code. Early on the AI confidently said "you can't win on even attempts," and it sounded right — but actually running the function showed the bug was different (the hints became nonsense, not the win). Next time I'll run the code to confirm a diagnosis before acting on it, rather than trusting a plausible-sounding explanation.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

AI-generated code can look polished and run without crashing while still being quietly, completely wrong — the hardest bugs here threw no errors at all. I now treat AI output as a confident first draft that I'm responsible for verifying, not as a finished answer.


## Finalized README and reflection documentation

Update README.md:
- Document Your Experience: game purpose, bugs found, and fixes applied
- Demo Walkthrough: step-by-step text walkthrough of a fixed game
  showing corrected hints, score updates, the win, and New Game reset
- Test Results: pytest output (12 passed)

Complete reflection.md:
- How AI was used as a teammate (one correct, one misleading suggestion)
- Debugging and testing approach (reproduce-the-bug-first tests)
- Explanation of Streamlit reruns and session state
- Developer habits and takeaways on verifying AI-generated code