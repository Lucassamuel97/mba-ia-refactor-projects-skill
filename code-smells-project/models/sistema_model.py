"""Consultas de estado da base usadas pelo health check."""


class SistemaModel:
    def __init__(self, obter_conexao):
        self._obter_conexao = obter_conexao

    def contagens(self):
        linha = self._obter_conexao().execute(
            "SELECT (SELECT COUNT(*) FROM produtos) AS produtos, "
            "(SELECT COUNT(*) FROM usuarios) AS usuarios, "
            "(SELECT COUNT(*) FROM pedidos) AS pedidos"
        ).fetchone()
        return dict(linha)
