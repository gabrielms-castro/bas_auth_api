from otp.crypto import decrypt
import pyotp
import re
import uuid
import logging

from django.db import models
from django.contrib.auth.models import User


# Configuração de logs
logger = logging.getLogger(__name__)


class Keys(models.Model):
    """
    Armazena chaves TOTP associadas a serviços.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="keys")
    nome_servico = models.CharField(max_length=100, verbose_name="Nome do Serviço")
    key = models.CharField(
        max_length=255,
        verbose_name="Chave TOTP",
        help_text="Chave secreta de 32 caracteres",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Chave TOTP"
        verbose_name_plural = "Chaves TOTP"
        ordering = ["nome_servico"]
    
    def __str__(self):
        return f"{self.nome_servico} - criado em {self.created_at:%Y-%m-%d %H:%M:%S}"
    
    @property
    def totp(self):
        """
        Inicializa o objeto TOTP apenas uma vez
        """
        try:
            return pyotp.TOTP(decrypt(self.key))
        except Exception as e:
            logger.error(f"Erro ao inicializar TOTP para '{self.nome_servico}': {e}")
            return None
    
    def generate_totp(self):
        """
        Gera o código TOTP baseado na chave armazenada
        """
        try:
            if not self.totp:
                raise ValueError("Chave TOTP inválida ou não inicializada")
            
            totp_code = self.totp.now()
            logger.info(f"TOTP gerado para o serviço '{self.nome_servico}': {totp_code}")

            return totp_code
        
        except Exception as e:
            logger.error(f"Erro ao gerar TOTP para o serviço '{self.nome_servico}': {e}")
            raise e
    
    def verify_totp(self, code):
        """
        Verifica a validade do código TOTP fornecido
        """
        try:
            is_valid = self.totp.verify(code)
            logger.info(f"Verificação de TOTP para o serviço '{self.nome_servico}': {'válido' if is_valid else 'inválido'}")
            return is_valid
        except Exception as e:
            logger.error(f"Erro ao verificar TOTP para o serviço '{self.nome_servico}': {e}")
            return False
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para remover espaços em branco da chave antes de salvar.
        """
        if self.key:
            self.key = self.key.replace(" ", "")
        super().save(*args, **kwargs)
