"""Acesso a dados de pedidos e itens de pedido."""

STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_ENVIADO = "enviado"
STATUS_ENTREGUE = "entregue"
STATUS_CANCELADO = "cancelado"
STATUS_VALIDOS = (STATUS_PENDENTE, STATUS_APROVADO, STATUS_ENVIADO, STATUS_ENTREGUE, STATUS_CANCELADO)

NOME_PRODUTO_REMOVIDO = "Desconhecido"


class PedidoModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def criar(self, usuario_id, total, itens):
        """Grava o pedido, os itens e a baixa de estoque em uma única transação.

        Cada item traz produto_id, quantidade e preco_unitario.
        """
        db = self._obter_conexao()
        with db:  # commit ao sair sem erro, rollback se houver exceção
            cursor = db.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
                (usuario_id, STATUS_PENDENTE, total),
            )
            pedido_id = cursor.lastrowid
            db.executemany(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)"
                " VALUES (?, ?, ?, ?)",
                [
                    (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
                    for item in itens
                ],
            )
            db.executemany(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                [(item["quantidade"], item["produto_id"]) for item in itens],
            )
        return pedido_id

    def listar(self, usuario_id=None):
        """Pedidos com seus itens, de todos os usuários ou de um só, em uma única query."""
        consulta = """
            SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                   i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
                   pr.id AS produto_encontrado, pr.nome AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido i ON i.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = i.produto_id
        """
        parametros = []
        if usuario_id is not None:
            consulta += " WHERE p.usuario_id = ?"
            parametros.append(usuario_id)
        linhas = self._obter_conexao().execute(consulta + " ORDER BY p.id, i.id", parametros).fetchall()

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
            if linha["item_id"] is None:
                continue
            produto_existe = linha["produto_encontrado"] is not None
            pedido["itens"].append({
                "produto_id": linha["produto_id"],
                "produto_nome": linha["produto_nome"] if produto_existe else NOME_PRODUTO_REMOVIDO,
                "quantidade": linha["quantidade"],
                "preco_unitario": linha["preco_unitario"],
            })
        return list(pedidos.values())

    def existe(self, pedido_id):
        linha = self._obter_conexao().execute(
            "SELECT 1 FROM pedidos WHERE id = ?", (pedido_id,)
        ).fetchone()
        return linha is not None

    def atualizar_status(self, pedido_id, novo_status):
        db = self._obter_conexao()
        with db:
            db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))

    def contar(self):
        return self._obter_conexao().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]

    def resumo_vendas(self):
        """Totais brutos de vendas. As regras do relatório ficam no service."""
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
