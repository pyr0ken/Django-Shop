from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationsForm, UserLoginForm
from django.contrib import messages
from .models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

class UserRegisterView(View):
    form_class = UserRegistrationsForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have already registered.', 'info')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                first_name=cd['first_name'],
                last_name=cd['last_name'],
                email=cd['email'],
                phone_number=cd['phone_number'],
                password=cd['password'],
            )
            user.save()
            login(request, user)
            messages.success(request, 'User registered.', 'success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have already logged in.', 'info')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'you logged in successfully. ', 'success')
            return redirect('home:home')
        messages.error(request, 'user is not registered !', 'danger')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        messages.success(request, 'user logged out successfully !', 'success')
        return redirect('home:home')
