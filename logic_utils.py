"""Pure game logic for the guessing game.

Refactored out of app.py so the rules can be unit-tested without Streamlit.
These functions take plain values and return plain values (no UI side effects).
"""


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        # Accept "42" and "42.0" but reject non-numeric text.
        value = int(float(raw)) if "." in raw else int(raw)
    except ValueError:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome as a string.

    Returns one of: "Win", "Too High", "Too Low".

    NOTE: this returns only the outcome. The human-facing hint text/emoji lives
    in the UI layer (app.py) so the logic stays presentation-free and testable.
    """
    # FIX: compare numerically. The starter version had a string-comparison
    # fallback that made "100" sort as less than "20".
    guess, secret = int(guess), int(secret)
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and which attempt this was (1-based)."""
    if outcome == "Win":
        # FIX: off-by-one. attempt_number is 1-based, so a first-guess win
        # should award the full 100 points (was 100 - 10*(attempt + 1)).
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: every wrong guess costs the same. The starter code secretly *added*
    # 5 points for a "Too High" guess on even attempts.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
