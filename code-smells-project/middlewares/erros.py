"""Exceções de domínio convertidas em resposta HTTP pelo handler central."""


class ErroAplicacao(Exception):
    status_code = 400

    def __init__(self, mensagem, **extras):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.extras = extras  # campos adicionais do corpo de erro, ex.: sucesso=False


class ErroValidacao(ErroAplicacao):
    status_code = 400


class ErroRegraNegocio(ErroAplicacao):
    status_code = 400


class ErroNaoAutenticado(ErroAplicacao):
    status_code = 401


class ErroAcessoNegado(ErroAplicacao):
    status_code = 403


class ErroNaoEncontrado(ErroAplicacao):
    status_code = 404


class ErroConflito(ErroAplicacao):
    status_code = 409
