"""Regras de cadastro e autenticação de usuários."""
import logging

from middlewares.erros import ErroRegraNegocio

logger = logging.getLogger(__name__)


class UsuarioService:
    def __init__(self, usuario_model, senhas):
        self._usuario_model = usuario_model
        self._senhas = senhas

    def criar_usuario(self, nome, email, senha):
        if self._usuario_model.existe_email(email):
            raise ErroRegraNegocio("Email já cadastrado")
        return self._usuario_model.criar(nome, email, self._senhas.gerar_hash(senha))

    def autenticar(self, email, senha):
        """Devolve os dados públicos do usuário, ou None se as credenciais não conferem."""
        # Bancos antigos podem ter mais de um cadastro com o mesmo email.
        for credencial in self._usuario_model.listar_credenciais(email=email):
            if self._senhas.verificar(credencial["senha"], senha):
                return {
                    "id": credencial["id"],
                    "nome": credencial["nome"],
                    "email": credencial["email"],
                    "tipo": credencial["tipo"],
                }
        return None

    def migrar_senhas_legadas(self):
        """Troca por hash as senhas que um banco antigo ainda guarda em texto puro."""
        migradas = 0
        for credencial in self._usuario_model.listar_credenciais():
            senha = credencial["senha"]
            if not isinstance(senha, str) or self._senhas.eh_hash(senha):
                continue
            self._usuario_model.atualizar_senha(credencial["id"], self._senhas.gerar_hash(senha))
            migradas += 1
        if migradas:
            logger.warning("%s senha(s) em texto puro foram convertidas para hash", migradas)
        return migradas
