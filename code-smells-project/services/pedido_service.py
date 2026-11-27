"""Casos de uso de pedido: criação com checagem de estoque e mudança de status."""
from middlewares.erros import ErroNaoEncontrado, ErroRegraNegocio


class PedidoService:
    def __init__(self, pedido_model, produto_model, usuario_model, notificacoes):
        self._pedido_model = pedido_model
        self._produto_model = produto_model
        self._usuario_model = usuario_model
        self._notificacoes = notificacoes

    def criar_pedido(self, usuario_id, itens):
        """`itens` é uma lista de dicionários com produto_id e quantidade, já validados."""
        if not self._usuario_model.existe(usuario_id):
            raise ErroRegraNegocio("Usuário não encontrado", sucesso=False)

        produtos = self._produto_model.buscar_por_ids(item["produto_id"] for item in itens)
        total = 0
        itens_do_pedido = []
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                raise ErroRegraNegocio(f"Produto {item['produto_id']} não encontrado", sucesso=False)
            if produto["estoque"] < item["quantidade"]:
                raise ErroRegraNegocio("Estoque insuficiente para " + produto["nome"], sucesso=False)
            total = total + (produto["preco"] * item["quantidade"])
            itens_do_pedido.append({
                "produto_id": item["produto_id"],
                "nome": produto["nome"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
            })

        pedido_id = self._pedido_model.criar(usuario_id, total, itens_do_pedido)
        self._notificacoes.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def atualizar_status(self, pedido_id, novo_status):
        if not self._pedido_model.existe(pedido_id):
            raise ErroNaoEncontrado("Pedido não encontrado")
        self._pedido_model.atualizar_status(pedido_id, novo_status)
        self._notificacoes.status_alterado(pedido_id, novo_status)
