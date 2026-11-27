"""Acesso a dados e regras da entidade usuário."""
from werkzeug.security import check_password_hash, generate_password_hash

TIPO_PADRAO = "cliente"
TIPO_ADMIN = "admin"

_COLUNAS_PUBLICAS = "id, nome, email, tipo, criado_em"


def _para_dict(linha):
    # A senha nunca faz parte da representação pública do usuário.
    return {
        "id": linha["id"],
        "nome": linha["nome"],
        "email": linha["email"],
        "tipo": linha["tipo"],
        "criado_em": linha["criado_em"],
    }


def _para_dict_login(linha):
    return {"id": linha["id"], "nome": linha["nome"], "email": linha["email"], "tipo": linha["tipo"]}


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
        return self._obter_conexao().execute(
            "SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone() is not None

    def email_cadastrado(self, email):
        return self._obter_conexao().execute(
            "SELECT 1 FROM usuarios WHERE email = ?", (email,)
        ).fetchone() is not None

    def autenticar(self, email, senha):
        """Devolve os dados de login do usuário se email e senha conferem; senão None."""
        linha = self._obter_conexao().execute(
            "SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        if linha is None or not check_password_hash(linha["senha"], senha):
            return None
        return _para_dict_login(linha)

    def criar(self, nome, email, senha):
        """Cadastro público: o tipo é sempre o padrão, independentemente do que foi enviado."""
        conexao = self._obter_conexao()
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, generate_password_hash(senha), TIPO_PADRAO),
            )
        return cursor.lastrowid
