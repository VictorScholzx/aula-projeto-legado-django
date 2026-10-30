import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse


def erro(mensagem, status):
    return JsonResponse({'error': mensagem}, status=status)


def metodo_nao_permitido():
    return erro('Método não permitido', 405)


def nao_encontrado(request, exception=None):
    return erro('Endpoint não encontrado', 404)


def erro_interno(request):
    return erro('Erro interno do servidor', 500)


def ler_json(request):
    """Retorna o corpo como dict; lança ValueError se o JSON for inválido."""
    dados = json.loads(request.body)
    if not isinstance(dados, dict):
        raise ValueError('O corpo deve ser um objeto JSON')
    return dados


def campo_faltando(dados, campos):
    """Retorna o primeiro campo ausente ou em branco, ou None."""
    for campo in campos:
        valor = dados.get(campo)
        if valor is None or not str(valor).strip():
            return campo
    return None


def para_id(valor):
    """Converte para inteiro; retorna None se o valor não for um ID válido."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def erro_de_campos(objeto):
    """Valida tamanhos e tipos (o SQLite não os impõe); retorna a mensagem do erro ou None."""
    try:
        objeto.clean_fields()
    except ValidationError as e:
        campo, mensagens = next(iter(e.message_dict.items()))
        return f"Campo '{campo}' inválido: {mensagens[0]}"
    return None
