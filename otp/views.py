from datetime import datetime

from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .models import Keys
from .serializers import GenerateTOTPSerializer


# Configuração de logs
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
            # Valida e salva o novo serviço
            new_key = Keys(user=request.user, nome_servico=nome_servico, key=key)
            new_key.full_clean()  # Valida o modelo, incluindo o Base32
            new_key.save()
            return redirect("home")
        except ValidationError as e:
            # Retorna o erro ao template
            return render(request, "novo_servico.html", {
                "error": e.message_dict.get("key", ["Erro desconhecido"])[0],
                "nome_servico": nome_servico,
                "key": key,
            })

    return render(request, "novo_servico.html")

@login_required
def editar_servico(request, pk):
    key_instance = Keys.objects.get(pk=pk, user=request.user)
    if request.method == "POST":
        nome_servico = request.POST.get("nome_servico")
        key = request.POST.get("key")
        try:
            # Atualiza e valida o serviço
            key_instance.nome_servico = nome_servico
            key_instance.key = key
            key_instance.full_clean()  # Valida o modelo
            key_instance.save()
            return redirect("home")
        
        except ValidationError as e:
            # Retorna o erro ao template
            return render(request, "editar_servico.html", {
                "key": key_instance,
                "error": e.message_dict.get("key", ["Erro desconhecido"])[0],
            })

    return render(request, "editar_servico.html", {"key": key_instance})


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
            "time_left": key.totp.interval - (datetime.now().timestamp() % key.totp.interval),
            "fetch_url": "/api/v1/totp/"  # URL da API para gerar o código
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
            return Response({"totp_code": totp_code}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Erro ao gerar TOTP: {e}")
            return Response({"error": "Erro ao gerar o TOTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)