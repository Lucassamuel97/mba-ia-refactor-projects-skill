"""Acesso a dados e regras da entidade produto."""

CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
CATEGORIA_PADRAO = "geral"
NOME_MIN = 2
NOME_MAX = 200

_COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def _para_dict(linha):
    return {
        "id": linha["id"],
        "nome": linha["nome"],
        "descricao": linha["descricao"],
        "preco": linha["preco"],
        "estoque": linha["estoque"],
        "categoria": linha["categoria"],
        "ativo": linha["ativo"],
        "criado_em": linha["criado_em"],
    }


class ProdutoModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def listar(self):
        linhas = self._obter_conexao().execute(f"SELECT {_COLUNAS} FROM produtos ORDER BY id").fetchall()
        return [_para_dict(linha) for linha in linhas]

    def buscar_por_id(self, produto_id):
        linha = self._obter_conexao().execute(
            f"SELECT {_COLUNAS} FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return _para_dict(linha) if linha else None

    def buscar_por_ids(self, produto_ids):
        """Devolve {id: produto} para os ids pedidos, em uma única query."""
        ids = sorted(set(produto_ids))
        if not ids:
            return {}
        marcadores = ", ".join("?" for _ in ids)
        linhas = self._obter_conexao().execute(
            f"SELECT {_COLUNAS} FROM produtos WHERE id IN ({marcadores})", ids
        ).fetchall()
        return {linha["id"]: _para_dict(linha) for linha in linhas}

    def buscar(self, termo, categoria=None, preco_min=None, preco_max=None):
        condicoes, parametros = [], []
        if termo:
            condicoes.append("(nome LIKE ? OR descricao LIKE ?)")
            parametros += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            condicoes.append("categoria = ?")
            parametros.append(categoria)
        if preco_min:
            condicoes.append("preco >= ?")
            parametros.append(preco_min)
        if preco_max:
            condicoes.append("preco <= ?")
            parametros.append(preco_max)
        filtro = " WHERE " + " AND ".join(condicoes) if condicoes else ""
        linhas = self._obter_conexao().execute(
            f"SELECT {_COLUNAS} FROM produtos{filtro} ORDER BY id", parametros
        ).fetchall()
        return [_para_dict(linha) for linha in linhas]

    def criar(self, nome, descricao, preco, estoque, categoria):
        conexao = self._obter_conexao()
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                (nome, descricao, preco, estoque, categoria),
            )
        return cursor.lastrowid

    def atualizar(self, produto_id, nome, descricao, preco, estoque, categoria):
        conexao = self._obter_conexao()
        with conexao:
            conexao.execute(
                "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
                (nome, descricao, preco, estoque, categoria, produto_id),
            )

    def excluir_sem_pedidos(self, produto_id):
        """Apaga o produto só se nenhum item de pedido o referencia. Devolve se apagou."""
        conexao = self._obter_conexao()
        with conexao:
            cursor = conexao.execute(
                "DELETE FROM produtos WHERE id = ? "
                "AND NOT EXISTS (SELECT 1 FROM itens_pedido WHERE produto_id = ?)",
                (produto_id, produto_id),
            )
        return cursor.rowcount > 0
