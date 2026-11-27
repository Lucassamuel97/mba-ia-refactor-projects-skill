"""Validação de entrada usada pelos controllers. Erros viram 400 no handler central."""
from middlewares.erros import ErroValidacao
from models.pedido_model import STATUS_VALIDOS
from models.produto_model import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_MAX, NOME_MIN


def _eh_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _eh_inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _eh_inteiro_positivo(valor):
    return _eh_inteiro(valor) and valor > 0


def validar_produto(dados):
    """Regra única para criação e atualização de produto. Devolve os campos normalizados."""
    if not isinstance(dados, dict) or not dados:
        raise ErroValidacao("Dados inválidos")
    if "nome" not in dados:
        raise ErroValidacao("Nome é obrigatório")
    if "preco" not in dados:
        raise ErroValidacao("Preço é obrigatório")
    if "estoque" not in dados:
        raise ErroValidacao("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ErroValidacao("Nome é obrigatório")
    if not _eh_numero(preco):
        raise ErroValidacao("Preço inválido")
    if not _eh_inteiro(estoque):
        raise ErroValidacao("Estoque inválido")
    if not isinstance(descricao, str) or not isinstance(categoria, str):
        raise ErroValidacao("Dados inválidos")

    if preco < 0:
        raise ErroValidacao("Preço não pode ser negativo")
    if estoque < 0:
        raise ErroValidacao("Estoque não pode ser negativo")
    if len(nome) < NOME_MIN:
        raise ErroValidacao("Nome muito curto")
    if len(nome) > NOME_MAX:
        raise ErroValidacao("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ErroValidacao("Categoria inválida. Válidas: " + str(list(CATEGORIAS_VALIDAS)))

    return nome, descricao, preco, estoque, categoria


def parametro_preco(valor_bruto, nome_parametro):
    if not valor_bruto:
        return None
    try:
        return float(valor_bruto)
    except ValueError:
        raise ErroValidacao(f"Parâmetro {nome_parametro} inválido") from None


def validar_credenciais(dados):
    dados = dados if isinstance(dados, dict) else {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not isinstance(email, str) or not isinstance(senha, str) or not email or not senha:
        raise ErroValidacao("Email e senha são obrigatórios")
    return email, senha


def validar_usuario(dados):
    if not isinstance(dados, dict) or not dados:
        raise ErroValidacao("Dados inválidos")
    campos = [dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")]
    if not all(isinstance(campo, str) and campo for campo in campos):
        raise ErroValidacao("Nome, email e senha são obrigatórios")
    return tuple(campos)


def validar_corpo_pedido(dados):
    if not isinstance(dados, dict) or not dados:
        raise ErroValidacao("Dados inválidos")
    return dados


def validar_usuario_id(dados):
    usuario_id = dados.get("usuario_id")
    if not _eh_inteiro_positivo(usuario_id):
        raise ErroValidacao("Usuario ID é obrigatório")
    return usuario_id


def validar_itens(dados):
    itens = dados.get("itens", [])
    if not itens:
        raise ErroValidacao("Pedido deve ter pelo menos 1 item")
    if not isinstance(itens, list):
        raise ErroValidacao("Itens inválidos")
    for item in itens:
        if (not isinstance(item, dict)
                or not _eh_inteiro_positivo(item.get("produto_id"))
                or not _eh_inteiro_positivo(item.get("quantidade"))):
            raise ErroValidacao("Itens inválidos")
    return [{"produto_id": item["produto_id"], "quantidade": item["quantidade"]} for item in itens]


def validar_status(dados):
    novo_status = dados.get("status", "") if isinstance(dados, dict) else ""
    if novo_status not in STATUS_VALIDOS:
        raise ErroValidacao("Status inválido")
    return novo_status
