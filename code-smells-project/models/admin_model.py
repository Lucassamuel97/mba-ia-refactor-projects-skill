"""Operações administrativas sobre a base inteira."""


class AdminModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def resetar_dados(self):
        conexao = self._obter_conexao()
        with conexao:
            conexao.execute("DELETE FROM itens_pedido")
            conexao.execute("DELETE FROM pedidos")
            conexao.execute("DELETE FROM produtos")
            conexao.execute("DELETE FROM usuarios")
