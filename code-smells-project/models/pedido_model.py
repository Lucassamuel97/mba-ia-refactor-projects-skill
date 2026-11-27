"""Acesso a dados da entidade pedido e de seus itens."""
from middlewares.erros import ErroRegraNegocio

STATUS_VALIDOS = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
STATUS_PENDENTE, STATUS_APROVADO, STATUS_CANCELADO = "pendente", "aprovado", "cancelado"
STATUS_INICIAL = STATUS_PENDENTE
PRODUTO_DESCONHECIDO = "Desconhecido"


class PedidoModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def criar(self, usuario_id, total, itens):
        """Grava pedido, itens e baixa de estoque numa única transação.

        `itens` traz produto_id, nome, quantidade e preco_unitario de cada item.
        A baixa só acontece se ainda houver estoque; caso contrário tudo é desfeito.
        """
        conexao = self._obter_conexao()
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
                (usuario_id, STATUS_INICIAL, total),
            )
            pedido_id = cursor.lastrowid
            for item in itens:
                baixa = conexao.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                    (item["quantidade"], item["produto_id"], item["quantidade"]),
                )
                if baixa.rowcount == 0:
                    raise ErroRegraNegocio("Estoque insuficiente para " + item["nome"], sucesso=False)
                conexao.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                    "VALUES (?, ?, ?, ?)",
                    (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
                )
        return pedido_id

    def listar(self, usuario_id=None):
        """Pedidos com seus itens em uma única query; filtra por usuário quando informado."""
        filtro, parametros = "", ()
        if usuario_id is not None:
            filtro, parametros = "WHERE p.usuario_id = ?", (usuario_id,)
        linhas = self._obter_conexao().execute(
            f"""
            SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                   i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
                   COALESCE(pr.nome, ?) AS produto_nome
              FROM pedidos p
              LEFT JOIN itens_pedido i ON i.pedido_id = p.id
              LEFT JOIN produtos pr ON pr.id = i.produto_id
              {filtro}
             ORDER BY p.id, i.id
            """,
            (PRODUTO_DESCONHECIDO, *parametros),
        ).fetchall()

        pedidos = {}
        for linha in linhas:
            pedido = pedidos.setdefault(linha["id"], {
                "id": linha["id"],
                "usuario_id": linha["usuario_id"],
                "status": linha["status"],
                "total": linha["total"],
                "criado_em": linha["criado_em"],
                "itens": [],
            })
            if linha["item_id"] is not None:
                pedido["itens"].append({
                    "produto_id": linha["produto_id"],
                    "produto_nome": linha["produto_nome"],
                    "quantidade": linha["quantidade"],
                    "preco_unitario": linha["preco_unitario"],
                })
        return list(pedidos.values())

    def existe(self, pedido_id):
        return self._obter_conexao().execute(
            "SELECT 1 FROM pedidos WHERE id = ?", (pedido_id,)
        ).fetchone() is not None

    def atualizar_status(self, pedido_id, novo_status):
        conexao = self._obter_conexao()
        with conexao:
            conexao.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))

    def resumo_vendas(self):
        """Contagens e soma do faturamento em uma única query."""
        linha = self._obter_conexao().execute(
            """
            SELECT COUNT(*) AS total_pedidos,
                   COALESCE(SUM(total), 0) AS faturamento,
                   COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS pendentes,
                   COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS aprovados,
                   COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS cancelados
              FROM pedidos
            """,
            (STATUS_PENDENTE, STATUS_APROVADO, STATUS_CANCELADO),
        ).fetchone()
        return dict(linha)
