def find_letter(letter, word):
    indexes = []
    for i in range(len(word)):
        if word[i] == letter:
            indexes.append(i)
    return indexes


def password_word(word_to_guess, used_letters):
    word_letters = word_to_guess.split('')
    used_letters = used_letters.split(',')
    hashed_word = []

    for letter in word_letters:
        hashed_word.append("_")

    for letter in used_letters:
        indexes = []
        for i in range(len(word_letters)):
            if word_letters[i] == letter:
                indexes.append(i)
        if indexes:
            for index in indexes:
                hashed_word[index] = letter
    breakpoint()
    current_guess = ''.join(hashed_word)
    return current_guess
