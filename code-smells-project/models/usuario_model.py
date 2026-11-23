"""Acesso a dados de usuários."""

TIPO_CLIENTE = "cliente"

# Campos públicos de um usuário. A senha nunca entra em respostas.
_CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")
_COLUNAS_PUBLICAS = ", ".join(_CAMPOS_PUBLICOS)


def _para_dict(linha):
    return {campo: linha[campo] for campo in _CAMPOS_PUBLICOS}


class UsuarioModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def listar(self):
        linhas = self._obter_conexao().execute(
            f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios ORDER BY id"
        ).fetchall()
        return [_para_dict(linha) for linha in linhas]

    def buscar_por_id(self, usuario_id):
        linha = self._obter_conexao().execute(
            f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return _para_dict(linha) if linha else None

    def existe(self, usuario_id):
        linha = self._obter_conexao().execute(
            "SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return linha is not None

    def existe_email(self, email):
        linha = self._obter_conexao().execute(
            "SELECT 1 FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        return linha is not None

    def listar_credenciais(self, email=None):
        """Uso interno da autenticação: inclui o hash da senha."""
        consulta = "SELECT id, nome, email, tipo, senha FROM usuarios"
        parametros = []
        if email is not None:
            consulta += " WHERE email = ?"
            parametros.append(email)
        linhas = self._obter_conexao().execute(consulta + " ORDER BY id", parametros).fetchall()
        return [dict(linha) for linha in linhas]

    def criar(self, nome, email, senha_hash):
        db = self._obter_conexao()
        with db:
            cursor = db.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, TIPO_CLIENTE),
            )
        return cursor.lastrowid

    def atualizar_senha(self, usuario_id, senha_hash):
        db = self._obter_conexao()
        with db:
            db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario_id))

    def contar(self):
        return self._obter_conexao().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
