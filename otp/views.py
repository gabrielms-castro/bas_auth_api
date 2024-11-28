from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Keys
from .serializers import GenerateTOTPSerializer
import logging

# Configuração de logs
logger = logging.getLogger(__name__)


class GenerateTOTP(APIView):
    """
    Gera o código TOTP com base em um serviço específico.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Valida a entrada do usuário
        serializer = GenerateTOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nome_servico = serializer.validated_data.get("nome_servico")
        usuario = serializer.validated_data.get("usuario")

        # Busca a chave do serviço
        try:
            key_instance = get_object_or_404(Keys, nome_servico=nome_servico)
        except Exception as e:
            logger.error(f"Erro ao buscar o serviço {nome_servico}: {e}")
            return Response(
                {"error": f"Serviço '{nome_servico}' não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        try:
            # Gera o código TOTP
            totp_code = key_instance.generate_totp()
            logger.info(f"TOTP gerado para o serviço '{nome_servico}' pelo usuário '{usuario}'.")
            
            # Retorna o TOTP gerado
            return Response(
                {
                    "nome_servico": nome_servico,
                    "usuario": usuario,
                    "totp_code": totp_code,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Erro ao gerar o TOTP para o serviço {nome_servico}: {e}")
            return Response(
                {"error": "Erro interno ao gerar o código TOTP."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
