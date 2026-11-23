"""Validação de entrada compartilhada pelos controllers."""
import math

from flask import request

from middlewares.erros import ErroValidacao

MENSAGEM_DADOS_INVALIDOS = "Dados inválidos"


def ler_corpo_json():
    """Corpo da requisição como dicionário.

    Corpo ausente, malformado, sem Content-Type JSON ou que não é um objeto vira 400.
    """
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroValidacao(MENSAGEM_DADOS_INVALIDOS)
    return dados


def exigir_numero(valor, mensagem):
    # bool é subclasse de int em Python e não conta como número aqui.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
        raise ErroValidacao(mensagem)
    return valor


def exigir_texto(valor, mensagem):
    if not isinstance(valor, str):
        raise ErroValidacao(mensagem)
    return valor


def converter_decimal(texto, campo):
    """Converte um parâmetro de query string em número."""
    try:
        numero = float(texto)
    except (TypeError, ValueError):
        raise ErroValidacao(f"{campo} inválido") from None
    if not math.isfinite(numero):
        raise ErroValidacao(f"{campo} inválido")
    return numero


def normalizar_id(valor, mensagem):
    """Aceita o id como inteiro ou como texto numérico, como a API sempre aceitou."""
    if isinstance(valor, bool):
        raise ErroValidacao(mensagem)
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float) and valor.is_integer():
        return int(valor)
    if isinstance(valor, str) and valor.strip().isdecimal():
        return int(valor.strip())
    raise ErroValidacao(mensagem)
