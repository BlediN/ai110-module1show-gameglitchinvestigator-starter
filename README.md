# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Purpose of the game.** A Streamlit number-guessing game: the app picks a secret number within a range that depends on difficulty (Easy 1–20, Normal 1–100, Hard 1–50). The player guesses, gets a "higher/lower" hint, and earns points — faster wins score more, wrong guesses cost points.

**Bugs found.**
- Hints were backwards — a guess that was too high told you to go *higher*.
- On every even-numbered attempt the secret was cast to a string, so guesses were compared as text (e.g. `100` was treated as smaller than `20`), producing nonsense hints.
- A wrong "Too High" guess on an even attempt secretly *added* 5 points instead of penalizing.
- Winning on the first guess only awarded 70 points (an off-by-one in the scoring formula).
- The "Attempts left" counter started one too low, and the banner always said "between 1 and 100" regardless of difficulty.
- "New Game" didn't reset the score or the won/lost status, so a finished game stayed stuck on "Game over."

**Fixes applied.**
- Refactored the four logic functions out of `app.py` into `logic_utils.py` so they can be unit-tested without Streamlit.
- `check_guess` now returns just the outcome and compares values as integers; the hint wording lives in a `HINT_MESSAGES` map in the UI with the corrected directions.
- `update_score` penalizes every wrong guess equally and uses a 1-based attempt count so a first-guess win is worth the full 100 points.
- Fixed the attempt counter initialization, the range banner, and made "New Game" reset all session state.
- Added pytest cases targeting each fixed bug.

## 📸 Demo Walkthrough

A sample Normal game (range 1–100, 8 attempts). The secret for this run, read from the **Developer Debug Info** panel, is **73**:

1. Start a new game — the banner reads "Guess a number between **1 and 100**. Attempts left: **8**", and the score is **0**.
2. User enters a guess of **40** → hint shows "📈 **Go HIGHER!**" (Too Low). Score drops to **−5**, attempts left: 7.
3. User enters a guess of **80** → hint shows "📉 **Go LOWER!**" (Too High). Score drops to **−10**, attempts left: 6.
4. User enters a guess of **73** → "🎉 **Correct!**" with balloons. Winning on the 3rd attempt awards **+80** points, so the final score is **70**.
5. The game reports "You won! The secret was 73. Final score: 70" and locks further guesses.
6. User clicks **New Game 🔁** → score resets to **0**, a fresh secret is drawn, and play resumes (the old "stuck on Game over" bug is gone).

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: ...\ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.14.0
collected 12 items

tests\test_game_logic.py ............                                    [100%]

============================= 12 passed in 0.05s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
