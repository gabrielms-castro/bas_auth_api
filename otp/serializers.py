from rest_framework import serializers

class GenerateTOTPSerializer(serializers.Serializer):
    """
    Valida os dados de entrada para gerar o código TOTP
    """
    
    nome_servico = serializers.CharField(max_length=100)
    usuario = serializers.CharField(max_length=100)
    senha = serializers.CharField(max_length=100)
    
    def validate_nome_servico(self, value):
        """
        Validação customizada para nome_servico
        """
        if not value:
            raise serializers.ValidationError("O campo 'nome_servico' é obrigatório")
        return value