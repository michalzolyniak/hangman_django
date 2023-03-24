from hangman_app.models import Game, WordsToGuess


class HangmanGame:
    def __init__(self, current_user, user_guess):
        self.current_user = current_user
        self.user_guess = user_guess
        self.user_game = Game.objects.filter(user_id=current_user, finish_game=False)
        if not self.user_game.exists():
            self.user_game = None
        else:
            self.user_game = Game.objects.get(user_id=current_user, finish_game=False)

        self.word_id = self.user_game.word_to_guess_id
        self.allowed_attempts = self.user_game.allowed_attempts
        self.current_guess = self.user_game.current_guess
        self.current_attempt = self.user_game.current_attempt
        self.word = self.get_user_word_to_guess()
        self.word_to_guess = self.user_game.word_to_guess.word
        self.used_letters = self.user_game.used_letters
        self.current_guess = self.user_game.current_guess
        self.letter_indexes = []

    def get_user_word_to_guess(self):
        word = WordsToGuess.objects.get(id=self.word_id).word
        return word

    def check_user_attempt(self):

        if len(self.user_guess) == 1:
            if self.used_letters:
                self.used_letters = self.used_letters.split(',')
                if self.user_guess not in self.used_letters:
                    self.used_letters.append(self.user_guess)
                    self.user_game.used_letters.sort()
                    self.used_letters = ",".join(self.used_letters)
                    self.letter_indexes = self.find_letter()
            else:
                self.used_letters = self.user_guess
                self.letter_indexes = self.find_letter()
            if self.letter_indexes:
                self.current_guess = self.password_word()

        if self.current_guess == self.word_to_guess or \
                self.user_guess == self.word_to_guess:
            self.update_user_game("win")
            return "win"

        self.current_attempt += 1
        if self.current_attempt > self.allowed_attempts:
            self.update_user_game("lost")
            return "lost"
        else:
            self.update_user_game("next_round")
            return "next_round"
        return None

    def update_user_game(self, action_type):
        if action_type == "win":
            self.user_game.win_game = True
            self.user_game.finish_game = True
        elif action_type == "lost":
            self.user_game.finish_game = True
        self.user_game.current_guess = self.current_guess
        self.user_game.current_attempt = self.current_attempt
        self.user_game.used_letters = self.used_letters
        self.user_game.save()

    def find_letter(self):

        indexes = []
        for i in range(len(self.word_to_guess)):
            if self.word_to_guess[i] == self.user_guess:
                indexes.append(i)
        return indexes

    def password_word(self):
        word_letters = [char for char in self.word_to_guess]
        used_letters = self.used_letters.split(',')
        hashed_word = []

        for index, letter in enumerate(word_letters):
            hashed_word.append("_")

        for letter in used_letters:
            indexes = []
            for i in range(len(word_letters)):
                if word_letters[i] == letter:
                    indexes.append(i)
            if indexes:
                for index in indexes:
                    hashed_word[index] = letter
        current_guess = ''.join(hashed_word)
        return current_guess
