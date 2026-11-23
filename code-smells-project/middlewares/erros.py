"""Exceções de domínio. O handler central as converte em respostas HTTP."""


class ErroAplicacao(Exception):
    status_code = 400

    def __init__(self, mensagem, extras=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        # Campos adicionais do corpo da resposta (ex.: {"sucesso": False}).
        self.extras = extras or {}


class ErroValidacao(ErroAplicacao):
    status_code = 400


class ErroRegraNegocio(ErroAplicacao):
    status_code = 400


class ErroNaoEncontrado(ErroAplicacao):
    status_code = 404


class ErroConsultaSql(ErroAplicacao):
    status_code = 400
