from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.utils.translation import gettext_lazy as _, ngettext

from django.contrib.auth.models import User
from .forms import UpdateAvatarForm
from .models import Profile

class HelloView(View):
    welcome_message = _("welcome hello world!")

    def get(self, request : HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        product_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        product_line = product_line.format(count=items)

        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{product_line}</h2>"
        )

class AboutMeView(UpdateView):
    model = Profile
    fields = ('avatar',)
    success_url = reverse_lazy('myauth:about-me')
    template_name = 'myauth/about-me.html'

    def get_object(self):
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            return Profile.objects.create(user=self.request.user)

class UpdateUserAvatarView(UserPassesTestMixin, UpdateView):
    model = Profile
    fields = ('avatar',)
    template_name = 'myauth/update_user_avatar.html'

    # Автоматически получаем профиль через URL (pk)
    def get_success_url(self):
        return reverse('myauth:user_profile', kwargs={'pk': self.object.user.pk})

    # Проверка прав: is_staff или владелец профиля
    def test_func(self):
        profile = self.get_object()
        return self.request.user.is_staff or self.request.user == profile.user


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