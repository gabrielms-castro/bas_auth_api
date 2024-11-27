from django.contrib import admin

from .models import Keys

@admin.register(Keys)
class KeysAdmin(admin.ModelAdmin):
    list_display = ("id", "nome_servico", "key", "created_at")
    search_fields = ("nome_servico",)
