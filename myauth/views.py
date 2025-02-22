from random import random
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, ListView
from django.views.decorators.cache import cache_page
from django.utils.translation import gettext_lazy as _, ngettext
from .models import Profile, User
from .forms import UserAvatarForm


class HelloView(View):
    welcome_message = _("welcome hello world!")
    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one products",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>",
            f"\n<h2>{products_line}</h2>"
        )


class UsersListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("myauth:login")
    template_name = "myauth/users-list.html"
    queryset = User.objects.all()
    context_object_name = "users"


class AboutMeView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy("myauth:login")
    template_name = "myauth/about-me.html"
    context_object_name = "user"
    model = User

    def get_object(self, queryset=None):
        print(self.request.GET.get("id"))
        if self.request.GET.get("id"):
            return User.objects.get(id=self.request.GET.get("id"))
        else:
            return User.objects.get(id=self.request.user.id)




class AvatarUpdateView(UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = UserAvatarForm
    template_name = "myauth/avatar-update.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        print(form)
        return response

    def test_func(self):
        if self.request.user.is_staff:
            return True
        self.object = self.get_object()
        return self.object.user_id == self.request.user.id

    def get_success_url(self):
        return reverse("myauth:about-me")


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


# def login_view(request: HttpRequest) -> HttpResponse:
#     if request.method == "GET":
#         if request.user.is_authenticated:
#             return redirect("/shop/orders/")
#         return render(request, "myauth/login.html")
#
#     username = request.POST["username"]
#     password = request.POST["password"]
#
#     user = authenticate(request, username=username, password=password)
#     if user:
#         login(request, user)
#         return redirect("/shop/orders/")
#     return render(request, "myauth/login.html", {"error": "Invalid login credentials"})
#
#
# def logout_view(request: HttpRequest):
#     logout(request)
#     return redirect(reverse("myauth:login"))


# class MyLogoutView(LogoutView):
#     next_page = reverse_lazy("myauth:login")

# class MyLoginView(LoginView):
#     next_page = reverse_lazy("myauth:about-me")

class MyLogoutView(TemplateView):
    template_name = "myauth/logout.html"

    def post(self, request):
        logout(request)
        return redirect(reverse("myauth:login"))

def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("bar", "lcd", max_age=3600)
    return response


@cache_page(120)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("bar", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")