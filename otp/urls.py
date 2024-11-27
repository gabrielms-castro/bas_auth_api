from django.urls import path

from .views import GenerateTOTP


urlpatterns = [
    path('totp/', GenerateTOTP.as_view(), name='totp'),
]