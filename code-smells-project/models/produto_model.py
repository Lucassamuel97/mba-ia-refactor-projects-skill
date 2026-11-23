"""Acesso a dados de produtos."""

CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
CATEGORIA_PADRAO = "geral"
NOME_TAMANHO_MINIMO = 2
NOME_TAMANHO_MAXIMO = 200

_CAMPOS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
_COLUNAS = ", ".join(_CAMPOS)


def _para_dict(linha):
    return {campo: linha[campo] for campo in _CAMPOS}


class ProdutoModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def listar(self):
        linhas = self._obter_conexao().execute(
            f"SELECT {_COLUNAS} FROM produtos ORDER BY id"
        ).fetchall()
        return [_para_dict(linha) for linha in linhas]

    def buscar_por_id(self, produto_id):
        linha = self._obter_conexao().execute(
            f"SELECT {_COLUNAS} FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return _para_dict(linha) if linha else None

    def buscar_por_ids(self, produto_ids):
        """Devolve os produtos encontrados em um dicionário indexado pelo id."""
        ids = list(set(produto_ids))
        if not ids:
            return {}
        marcadores = ", ".join("?" for _ in ids)
        linhas = self._obter_conexao().execute(
            f"SELECT {_COLUNAS} FROM produtos WHERE id IN ({marcadores})", ids
        ).fetchall()
        return {linha["id"]: _para_dict(linha) for linha in linhas}

    def buscar(self, termo, categoria=None, preco_min=None, preco_max=None):
        condicoes, parametros = ["1=1"], []
        if termo:
            condicoes.append("(nome LIKE ? OR descricao LIKE ?)")
            parametros.extend([f"%{termo}%", f"%{termo}%"])
        if categoria:
            condicoes.append("categoria = ?")
            parametros.append(categoria)
        if preco_min:
            condicoes.append("preco >= ?")
            parametros.append(preco_min)
        if preco_max:
            condicoes.append("preco <= ?")
            parametros.append(preco_max)
        linhas = self._obter_conexao().execute(
            f"SELECT {_COLUNAS} FROM produtos WHERE " + " AND ".join(condicoes) + " ORDER BY id",
            parametros,
        ).fetchall()
        return [_para_dict(linha) for linha in linhas]

    def criar(self, nome, descricao, preco, estoque, categoria):
        db = self._obter_conexao()
        with db:
            cursor = db.execute(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                (nome, descricao, preco, estoque, categoria),
            )
        return cursor.lastrowid

    def atualizar(self, produto_id, nome, descricao, preco, estoque, categoria):
        db = self._obter_conexao()
        with db:
            db.execute(
                "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
                (nome, descricao, preco, estoque, categoria, produto_id),
            )

    def deletar(self, produto_id):
        db = self._obter_conexao()
        with db:
            db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))

    def contar(self):
        return self._obter_conexao().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
