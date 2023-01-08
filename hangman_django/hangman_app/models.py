from django.db import models
from django.conf import settings

COUNTRY = (
    (1, "PL"),
    (2, "UK"),
    (3, "USA"),
)


class WordsToGuess(models.Model):
    """
        words to guesess database
    """
    word = models.CharField(unique=True, max_length=64)
    country = models.IntegerField(choices=COUNTRY, null=True)


class Game(models.Model):
    """
        Hangman game per user
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word_to_guess = models.ForeignKey(WordsToGuess, on_delete=models.CASCADE)
    used_letters = models.CharField(max_length=64)
    current_attempt = models.IntegerField()
    allowed_attempts = models.IntegerField()
    game_date = models.DateTimeField()


class GuessedWords(models.Model):
    """
        Guessed words per user
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    guessed_word = models.ForeignKey(WordsToGuess, on_delete=models.CASCADE)
    guessed = models.BooleanField()
    guessed_attempt = models.IntegerField()
    allowed_attempts = models.IntegerField()
    game_date = models.DateTimeField()

