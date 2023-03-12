from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, \
    authenticate, logout
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
# Create your views here.
from django.views.generic import FormView
from .forms import UserCreateForm, LoginForm, GameForm, MainForm
from django.views import View
from hangman_app.models import get_random_word_for_country, Game, WordsToGuess, \
    get_user_word_to_guess
from datetime import datetime

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
            current_user = request.user
            Game.objects.create(
                user=current_user,
                word_to_guess=word_to_guess,
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
        user_game = Game.objects.get(user_id=current_user)
        word_id = user_game.word_to_guess_id
        word = "test"
        allowed_attempts = user_game.allowed_attempts
        current_attempt = user_game.current_attempt
        # word = get_user_word_to_guess(word_id)
        word_len = len(word)
        password_word = word_len * " _"
        context = {'form': form, 'password_word': password_word,
                   'allowed_attempts': allowed_attempts,
                   'current_attempt': current_attempt}
        return render(request, 'hangman_django/game.html', context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        context = {'form': form}
        if form.is_valid():
            cd = form.cleaned_data
            word = cd['word']
            user_game = Game.objects.get(user_id=current_user)

    #        consumption_hours = cd['consumption_hours']
    #         default_price = 1
    #         categories = cd['category']
    #         product = Product.objects.create(
    #             name=name,
    #             consumption_hours=consumption_hours,
    #             default_price=default_price
    #         )
    #
    #         for category in categories:
    #             product.category.add(category)
    #
    #         return redirect('fridge')
    #     return render(request, 'fridge/add_category.html', context)
