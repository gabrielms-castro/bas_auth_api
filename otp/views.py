from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.shortcuts import redirect, render, get_object_or_404

from otp.crypto import decrypt, encrypt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Keys
from .serializers import GenerateTOTPSerializer


import logging
logger = logging.getLogger(__name__)



def logout_view(request):
    logout(request)
    return redirect("/")

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            error = "Usuário ou senha inválidos."

    return render(request, "login.html", {"error": error})

@login_required
def novo_servico(request):
    if request.method == "POST":
        nome_servico = request.POST.get("nome_servico")
        key = request.POST.get("key")
        try:
            new_key = Keys(user=request.user, nome_servico=nome_servico, key=encrypt(key))
            new_key.full_clean()
            new_key.save()
            return redirect("home")
        except ValidationError as e:
            return render(request, "novo_servico.html", {
                "error": e.message_dict.get("key", ["Erro desconhecido"])[0],
                "nome_servico": nome_servico,
                "key": key,
            })
        except Exception as e:
            return render(request, "novo_servico.html", {
                "error": e.message_dict.get("key", ["Erro desconhecido"])[0]
            })

    return render(request, "novo_servico.html")

@login_required
def editar_servico(request, pk):
    key_instance = Keys.objects.get(pk=pk, user=request.user)
    
    if request.method == "POST":
        nome_servico = request.POST.get("nome_servico")
        key = request.POST.get("key")

        try:
            key_instance.nome_servico = nome_servico
            key_instance.key = encrypt(key)
            key_instance.full_clean()
            key_instance.save()

            return redirect("home")
        
        except ValidationError as e:
            return render(request, "editar_servico.html", {
                "key": key_instance,
                "error": e.message_dict.get("key", ["Erro desconhecido"])[0],
            })

    return render(request, "editar_servico.html", {
        "nome_servico": key_instance.nome_servico,
        "key": decrypt(key_instance.key)
    })


@login_required
def excluir_servico(request, pk):
    key = get_object_or_404(Keys, pk=pk, user=request.user)
    key.delete()
    return redirect("home")


@login_required
def home_page(request):
    keys = Keys.objects.filter(user=request.user)
    services = [
        {
            "id": key.id,
            "nome_servico": key.nome_servico,
            "totp_code": key.generate_totp(),
            "time_left": key.time_left,
            "fetch_url": "/api/v1/totp/"
        }
        for key in keys
    ]
    return render(request, "home.html", {"user": request.user, "services": services})


class GenerateTOTP(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = GenerateTOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)    
        nome_servico = request.data.get("nome_servico")
        user = request.user
        
        # Busca serviço associado ao usuário
        key_instance = get_object_or_404(Keys, user=user, nome_servico=nome_servico)

        try:
            totp_code = key_instance.generate_totp()
            time_left = key_instance.time_left
            return Response({"totp_code": totp_code, "time_left":time_left}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Erro ao gerar TOTP: {e}")
            return Response({"error": "Erro ao gerar o TOTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
