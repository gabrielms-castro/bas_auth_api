from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Keys
from .serializers import GenerateTOTPSerializer


class GenerateTOTP(APIView):
    """
    Gera o codigo TOTP
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        # Valida a entrada
        serializer = GenerateTOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Recupera o serviço com base no nome fornecido
        nome_servico = serializer.validated_data.get("nome_servico")
        key_instance = get_object_or_404(Keys, nome_servico=nome_servico)
        
        # Gera o código TOTP
        totp_code = key_instance.generate_totp()
        
        # Retorna o código gerado
        return Response(
            {
                "nome_servico": nome_servico,
                "usuario": serializer.validated_data.get("usuario"),
                "totp_code": totp_code
            },
            status = status.HTTP_200_OK
        )