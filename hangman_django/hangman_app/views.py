from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, \
    authenticate, logout
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView
from datetime import datetime
from .forms import UserCreateForm, LoginForm, GameForm, MainForm
from django.views import View
from hangman_app.models import get_random_word_for_country, Game
from hangman_app.game_class import HangmanGame
from django.db.models import Sum

User = get_user_model()


class UserCreateView(FormView):
    """
        User create view
    """
    template_name = 'hangman_django/user_create.html'
    form_class = UserCreateForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        cd = form.cleaned_data
        User.objects.create_user(
            username=cd['login'],
            password=cd['password1'],
            email=cd['email'],
        )
        return response


class LoginView(FormView):
    """
        Login view
    """
    template_name = 'hangman_django/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('game')

    def form_valid(self, form):
        response = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['login'], password=cd['password'])
        login(self.request, user)
        return response


class LogoutView(RedirectView):
    """
        Logout view
    """
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class MainView(LoginRequiredMixin, View):
    """
        Game create view
    """
    form_class = MainForm

    def get(self, request, *args, **kwargs):
        current_user = request.user
        user_game = HangmanGame(current_user, None)
        if user_game.user_game_exist:
            return redirect('game')
        else:
            form = self.form_class()
            context = {'form': form}
            return render(request, 'hangman_django/main.html', context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            language = int(cd['language'])
            attempts = int(cd['attempts'])
            word_to_guess = get_random_word_for_country(language)
            word_len = len(word_to_guess.word)
            hashed_word = word_len * "_"
            current_user = request.user
            Game.objects.create(
                user=current_user,
                word_to_guess=word_to_guess,
                current_guess=hashed_word,
                used_letters="",
                current_attempt=1,
                allowed_attempts=attempts,
                game_date=datetime.now()
            )
        return redirect('game')


class GameView(LoginRequiredMixin, View):
    """
        Game view
    """
    form_class = GameForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        current_user = request.user
        user_game = HangmanGame(current_user, None)
        if not user_game.user_game_exist:
            return redirect('main')
        else:
            context = {'form': form, 'word': user_game.word, 'hashed_word': user_game.current_guess,
                       'allowed_attempts': user_game.allowed_attempts,
                       'current_attempt': user_game.current_attempt,
                       'word_length': user_game.word_length
                       }
            return render(request, 'hangman_django/game.html', context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user_guess = str(cd['word'])
            current_user = request.user
            user_game = HangmanGame(current_user, user_guess)
            if not user_game.user_game:
                return redirect('main')
            game_status = user_game.update_user_game()
            if game_status == "win":
                message = "You win!"
                context = {'form': form, 'word': user_game.word_to_guess, 'message': message}
                return render(request, 'hangman_django/message.html', context)
            elif game_status == "lost":
                message = "You lost!"
                context = {'form': form, 'word': user_game.word_to_guess, 'message': message}
                return render(request, 'hangman_django/message.html', context)
            else:
                form = self.form_class()
                context = {'form': form, 'word': user_game.word_to_guess,
                           'hashed_word': user_game.current_guess,
                           'allowed_attempts': user_game.allowed_attempts,
                           'current_attempt': user_game.current_attempt,
                           'used_letters': user_game.used_letters,
                           'word_length': user_game.word_length}
                return render(request, 'hangman_django/game.html', context)


class UserStatView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        played_games = Game.objects.filter(user=request.user.id, finish_game=True).count()
        wins = Game.objects.filter(user=request.user.id, win_game=True).count()
        loses = Game.objects.filter(user=request.user.id, finish_game=True, win_game=False).count()
        guessed_words = Game.objects.filter(user=request.user.id, win_game=True)
        not_guessed_words = Game.objects.filter(user=request.user.id, finish_game=True, win_game=False)
        guessed_words_show = [word.word_to_guess.word for word in guessed_words]
        guessed_words_show.sort()
        guessed_words_show = ','.join(guessed_words_show)
        not_guessed_words_show = [word.word_to_guess.word for word in not_guessed_words]
        not_guessed_words_show.sort()
        not_guessed_words_show = ','.join(not_guessed_words_show)
        context = {"played_games": played_games,
                   "wins": wins,
                   "loses": loses,
                   "guessed_words": guessed_words_show,
                   "not_guessed_words": not_guessed_words_show
                   }
        return render(request, 'hangman_django/user_stats.html', context)
