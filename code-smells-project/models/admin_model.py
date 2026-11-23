"""Operações administrativas sobre o banco. Só são alcançáveis pelas rotas protegidas."""
import sqlite3

from middlewares.erros import ErroConsultaSql

# Filhos antes dos pais.
_COMANDOS_RESET = (
    "DELETE FROM itens_pedido",
    "DELETE FROM pedidos",
    "DELETE FROM produtos",
    "DELETE FROM usuarios",
)


class AdminModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def resetar_dados(self):
        db = self._obter_conexao()
        with db:
            for comando in _COMANDOS_RESET:
                db.execute(comando)

    def consultar(self, sql):
        """Executa uma consulta e devolve as linhas."""
        try:
            linhas = self._obter_conexao().execute(sql).fetchall()
        except sqlite3.Error as erro:
            raise ErroConsultaSql(str(erro)) from erro
        return [dict(linha) for linha in linhas]

    def executar(self, sql):
        """Executa um comando de escrita e confirma a transação."""
        db = self._obter_conexao()
        try:
            with db:
                db.execute(sql)
        except sqlite3.Error as erro:
            raise ErroConsultaSql(str(erro)) from erro
