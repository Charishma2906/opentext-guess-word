def evaluate_guess(answer, guess):
    """
    answer: correct word (5-letter uppercase)
    guess: guessed word (5-letter uppercase)
    Returns: list like ['green', 'grey', 'orange', ...]
    """
    answer_chars = list(answer)
    result = ['grey'] * 5

    # pass 1: exact matches
    for i in range(5):
        if guess[i] == answer_chars[i]:
            result[i] = 'green'
            answer_chars[i] = None

    # pass 2: present but wrong place
    for i in range(5):
        if result[i] == 'green':
            continue
        if guess[i] in answer_chars:
            result[i] = 'orange'
            answer_chars[answer_chars.index(guess[i])] = None

    return result
