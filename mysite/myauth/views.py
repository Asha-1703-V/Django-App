from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView

from django.contrib.auth.models import User
from .forms import UpdateAvatarForm
from .models import Profile

class AboutMeView(UpdateView):
    model = Profile
    fields = ('avatar',)
    success_url = reverse_lazy('about-me')

    def get_object(self):
        return self.request.user.profile

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response

@login_required
def about_me(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UpdateAvatarForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('about_me')
    else:
        form = UpdateAvatarForm(instance=user_profile)

    return render(request, 'myauth/about-me.html', {'user_profile': user_profile, 'form': form})

def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))

class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")

class MyLogoutPage(View):
    def get(self, request):
        logout(request)
        return redirect('myauth:login')

@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")

@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")

@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")

class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})

def users_list(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'myauth/users_list.html', {'users': users})

def user_profile(request, pk):
    user = User.objects.get(pk=pk)
    try:
        user_profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        user_profile = None

    return render(request, 'myauth/user_profile.html', {'user': user, 'user_profile': user_profile})

@user_passes_test(lambda u: u.is_staff or u.pk == pk)
def update_user_avatar(request, pk):
    user = User.objects.get(pk=pk)
    try:
        user_profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        if user_profile:
            form = UpdateAvatarForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                return redirect('myauth:user_profile', pk=pk)
        else:
            return HttpResponse("Профиль не найден")
    else:
        if user_profile:
            form = UpdateAvatarForm(instance=user_profile)
        else:
            form = None

    return render(request, 'myauth/update_user_avatar.html', {'form': form, 'user': user})

class UsersListView(ListView):
    model = User
    template_name = 'myauth/users_list.html'
    context_object_name = 'users'

class UserProfileView(DetailView):
    model = User
    template_name = 'myauth/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_profile = Profile.objects.get(user=self.object)
        except Profile.DoesNotExist:
            user_profile = None
        context['user_profile'] = user_profile
        return context