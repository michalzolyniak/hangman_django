from django.db import models
from django.conf import settings
import pandas as pd

COUNTRY = (
    (1, "PL"),
    (2, "UK"),
    (3, "USA"),
)


class WordsToGuess(models.Model):
    """
        words to guess database
    """
    word = models.CharField(unique=True, max_length=64)
    country = models.IntegerField(choices=COUNTRY, null=True)


class Game(models.Model):
    """
        Hangman game per ser
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word_to_guess = models.ForeignKey(WordsToGuess, on_delete=models.CASCADE)
    current_guess = models.CharField(max_length=64, default=False)
    used_letters = models.CharField(max_length=64)
    current_attempt = models.IntegerField()
    allowed_attempts = models.IntegerField()
    game_date = models.DateTimeField()
    win_game = models.BooleanField(default=False)
    finish_game = models.BooleanField(default=False)


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


def import_polish_words():
    print('start')
    df_words = pd.read_fwf('/home/michalzolyniak/Desktop/coders_lab/hangman_django/polish_words.txt')
    df_words.columns = ['word']
    df_words['country'] = '1'
    df_words = df_words.head(1000)
    data = df_words.to_dict('records')
    model_instances = [WordsToGuess(**row) for row in data]
    # bulk create the model instances
    WordsToGuess.objects.bulk_create(model_instances)
    print('finish')
    # return None
    # from hangman_app.models import import_polish_words


def get_random_word_for_country(country):
    """
    Returns a single random word from the WordsToGuess model for the given country.
    """
    words = WordsToGuess.objects.filter(country=country).order_by('?')
    if words.exists():
        return words.first()
    else:
        return None


def get_user_word_to_guess(word_id):
    word = WordsToGuess.objects.get(id=word_id).word
    return word


def test_word():
    data = WordsToGuess.objects.get(id=1)
    return data
