from django.contrib import admin
from django.urls import path, include
from otp.views import home_page, login_view, logout_view

urlpatterns = [
    # Administração
    path("admin/", admin.site.urls),

    # Autenticação e Views principais
    path("", login_view, name="login"),  # Página inicial/login
    path("home/", home_page, name="home"),  # Página principal do usuário logado
    path("logout/", logout_view, name="logout"),  # Logout do usuário

    # APIs
    path("api/v1/", include("otp.urls")),  # Rotas do app OTP na API
    path("api/v1/", include("authentication.urls")),  # Rotas de autenticação na API
]