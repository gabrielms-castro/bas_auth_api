import pyotp
import re
import uuid

from django.db import models
from django.core.exceptions import ValidationError


def validate_base32_key(value):
    """
    Valida se o valor fornecido está no formato Base32 válido.
    """
    if not re.fullmatch(r"[A-Z2-7]+", value.replace(" ", "")):
        raise ValidationError("A chave TOTP deve estar no formato Base32 (Apenas letras de A-Z e dígitos 2-7).")


class Keys(models.Model):
    """
    Armazenar chaves TOTP associadas a serviços.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_servico = models.CharField(max_length=100, verbose_name="Nome do Serviço")
    key = models.CharField(
        max_length=100,
        verbose_name="Chave TOTP",
        help_text="Chave secreta de 32 caracteres",
        validators=[validate_base32_key],
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
        return pyotp.TOTP(self.key)
    
    def generate_totp(self):
        """
        Gera o código TOTP baseada na chave armazenada
        """
        return self.totp.now()
    
    def verify_totp(self, code):
        """
        Verifica a validade do código TOTP fornecido é válido
        """
        return self.totp.verify(code)
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para remover espaços em branco da chave antes de salvar.
        """
        if self.key:
            # Remove espaços em branco antes de salvar
            self.key = self.key.replace(" ", "")
        super().save(*args, **kwargs)    