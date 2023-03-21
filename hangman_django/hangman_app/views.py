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
from hangman_app.models import get_random_word_for_country, Game, WordsToGuess, \
    get_user_word_to_guess
from hangman_app.game_logic import find_letter, password_word

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
        Product create view
    """
    form_class = MainForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, 'hangman_django/main.html', context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        # context = {'form': form}
        if form.is_valid():
            cd = form.cleaned_data
            language = int(cd['language'])
            attempts = int(cd['attempts'])
            word_to_guess = get_random_word_for_country(language)
            word_len = len(word_to_guess.word)
            hashed_word = word_len * " _"
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
        Product create view
    """
    form_class = GameForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        current_user = request.user
        user_game = Game.objects.filter(user_id=current_user, finish_game=False)
        if not user_game.exists():
            return redirect('main')
        else:
            user_game = Game.objects.get(user_id=current_user, finish_game=False)
        word_id = user_game.word_to_guess_id
        allowed_attempts = user_game.allowed_attempts
        current_guess = user_game.current_guess
        current_attempt = user_game.current_attempt
        word = get_user_word_to_guess(word_id)
        context = {'form': form, 'word': word, 'hashed_word': current_guess,
                   'allowed_attempts': allowed_attempts,
                   'current_attempt': current_attempt}
        return render(request, 'hangman_django/game.html', context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        context = {'form': form}
        if form.is_valid():
            current_user = request.user
            user_game = Game.objects.filter(user_id=current_user, finish_game=False)
            if not user_game.exists():
                return redirect('main')
            else:
                user_game = Game.objects.get(user_id=current_user, finish_game=False)
            letter_indexes = []
            user_game = Game.objects.get(user_id=current_user, finish_game=False)
            word_to_guess = user_game.word_to_guess.word
            used_letters = user_game.used_letters
            current_guess = user_game.current_guess
            cd = form.cleaned_data
            user_guess = str(cd['word'])
            current_attempt = user_game.current_attempt
            allowed_attempts = user_game.allowed_attempts
            if len(user_guess) == 1:
                if used_letters:
                    used_letters = used_letters.split(',')
                    if user_guess not in used_letters:
                        used_letters.append(user_guess)
                        used_letters.sort()
                        used_letters = ",".join(used_letters)
                        letter_indexes = find_letter(user_guess, word_to_guess)
                else:
                    used_letters = user_guess
                    letter_indexes = find_letter(user_guess, word_to_guess)
                if letter_indexes:
                    current_guess = password_word(word_to_guess, used_letters)

        if current_guess == word_to_guess or \
                user_guess == word_to_guess:
            user_game.current_guess = current_guess
            user_game.current_attempt = current_attempt
            user_game.used_letters = used_letters
            user_game.win_game = True
            user_game.finish_game = True
            user_game.save()
            message = "You win!"
            context = {'form': form, 'word': word_to_guess, 'message': message}
            return render(request, 'hangman_django/message.html', context)

        current_attempt += 1
        if current_attempt > allowed_attempts:
            user_game.current_guess = current_guess
            user_game.current_attempt = current_attempt
            user_game.used_letters = used_letters
            user_game.finish_game = True
            user_game.save()
            message = "You lost!"
            context = {'form': form, 'word': word_to_guess, 'message': message}
            return render(request, 'hangman_django/message.html', context)
        else:
            user_game.current_guess = current_guess
            user_game.current_attempt = current_attempt
            user_game.used_letters = used_letters
            user_game.save()
            context = {'form': form, 'word': word_to_guess, 'hashed_word': current_guess,
                       'allowed_attempts': allowed_attempts,
                       'current_attempt': current_attempt,
                       'used_letters': used_letters}
            return render(request, 'hangman_django/game.html', context)
