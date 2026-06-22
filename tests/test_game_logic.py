from logic_utils import (
    check_guess,
    update_score,
    parse_guess,
    get_range_for_difficulty,
)


# --- Starter tests: check_guess returns the correct outcome ---

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# --- Bug fix: even-attempt string comparison ---
# The old code compared the secret as a string on even attempts, so 100 was
# treated as smaller than 20. A guess of 100 vs secret 20 must be "Too High".

def test_large_guess_is_not_treated_as_small_string():
    assert check_guess(100, 20) == "Too High"


# --- Bug fix: wrong guesses must never increase the score ---

def test_too_high_does_not_add_points_on_even_attempt():
    # attempt 2 is even -- the buggy version returned current_score + 5 here.
    assert update_score(0, "Too High", 2) == -5


def test_too_low_decreases_score():
    assert update_score(10, "Too Low", 3) == 5


# --- Bug fix: winning on the first guess awards full points ---

def test_first_guess_win_awards_full_points():
    assert update_score(0, "Win", 1) == 100


def test_win_points_decrease_with_more_attempts():
    assert update_score(0, "Win", 2) == 90


def test_win_points_floor_at_10():
    # Even a very slow win should still be worth at least 10 points.
    assert update_score(0, "Win", 20) == 10


# --- Supporting logic ---

def test_parse_guess_valid_integer():
    assert parse_guess("42") == (True, 42, None)


def test_parse_guess_rejects_non_numeric():
    ok, value, err = parse_guess("hello")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_range_for_each_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)


# --- Challenge 1: Advanced edge-case testing ---
# These inputs are unusual but plausible. The game should handle them
# gracefully (parse or reject cleanly, compare correctly) and never crash.

def test_negative_number_is_handled_gracefully():
    # A negative guess should parse and compare as a normal (low) number.
    ok, value, err = parse_guess("-5")
    assert (ok, value, err) == (True, -5, None)
    assert check_guess(-5, 50) == "Too Low"


def test_decimal_input_is_truncated_not_crashing():
    # Decimals are accepted and truncated toward zero, not rejected/crashed.
    assert parse_guess("42.9") == (True, 42, None)
    assert parse_guess("-3.7") == (True, -3, None)


def test_extremely_large_value_does_not_overflow():
    # Python ints are arbitrary precision, so a huge guess must still work.
    big = 10 ** 18
    assert parse_guess(str(big)) == (True, big, None)
    assert check_guess(big, 50) == "Too High"


def test_whitespace_padded_number_is_accepted():
    assert parse_guess("  42  ") == (True, 42, None)


def test_scientific_notation_is_rejected_cleanly():
    # "1e5" isn't a plain integer; reject with the friendly message, no crash.
    ok, value, err = parse_guess("1e5")
    assert ok is False
    assert value is None
    assert err == "That is not a number."
