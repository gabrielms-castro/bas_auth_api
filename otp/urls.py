from django.urls import path
from . import views

app_name = "otp"  # Namespace para evitar conflitos de nomes em outros apps

urlpatterns = [
    # API
    path("totp/", views.GenerateTOTP.as_view(), name="generate_totp"),  # Geração de TOTP via API
    path("editar-servico/<uuid:pk>/", views.editar_servico, name="editar_servico"),  # Nova rota para edição
    path("novo-servico/", views.novo_servico, name="novo_servico"),  # Cadastro de novo serviço (via API)
    path("excluir-servico/<uuid:pk>/", views.excluir_servico, name="excluir_servico"),  # Excluir serviço via API
]
