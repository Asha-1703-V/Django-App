from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView

from django.contrib.auth.models import User
from .forms import UpdateAvatarForm
# from .models import Profile
from .models import UserProfile
from django.shortcuts import render, redirect


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        UserProfile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


# def login_view(request: HttpRequest) -> HttpResponse:
#     if request.method == "GET":
#         if request.user.is_authenticated:
#             return redirect('/admin/')
#
#         return render(request, 'myauth/login.html')
#
#     username = request.POST["username"]
#     password = request.POST["password"]
#
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return  redirect("/admin/")
#
#     return render(request, "myauth/login.html", {"error": "Invalid login credentails"})

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

@login_required
def about_me(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = UpdateAvatarForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('about_me')
    else:
        form = UpdateAvatarForm(instance=user_profile)

    return render(request, 'about_me.html', {'user_profile': user_profile, 'form': form})

def users_list(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'myauth/users_list.html', {'users': users})

def user_profile(request, pk):
    user = User.objects.get(pk=pk)
    user_profile = UserProfile.objects.filter(user=user).first()
    return render(request, 'myauth/user_profile.html', {'user': user, 'user_profile': user_profile})

@user_passes_test(lambda u: u.is_staff)
def update_user_avatar(request, pk):
    user = User.objects.get(pk=pk)
    user_profile = UserProfile.objects.filter(user=user).first()
    if request.method == 'POST':
        form = UpdateAvatarForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', pk=pk)
    else:
        form = UpdateAvatarForm(instance=user_profile)

    return render(request, 'myauth/update_user_avatar.html', {'form': form, 'user': user})