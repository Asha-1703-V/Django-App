from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    MyLogoutPage,
    AboutMeView,
    RegisterView,
    FooBarView,
    update_user_avatar,
    UsersListView,
    UserProfileView,
    UpdateUserAvatarView,
    HelloView,
)

app_name = "myauth"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("hello/", HelloView.as_view(), name="hello"),
    path("users/", UsersListView.as_view(), name="users_list"),
    path("users/<int:pk>/", UserProfileView.as_view(), name="user_profile"),
    path("users/<int:pk>/update-avatar/", UpdateUserAvatarView.as_view(), name="update_user_avatar"),
    path("logout/", MyLogoutPage.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),

    path("session/set/", set_session_view, name="session-set"),
    path("session/get/", get_session_view, name="session-get"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]
