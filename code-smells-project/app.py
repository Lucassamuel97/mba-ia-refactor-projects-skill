"""Composition root: cria a aplicação, liga as camadas e inicia o servidor."""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from controllers.admin_controller import AdminController
from controllers.pedido_controller import PedidoController
from controllers.produto_controller import ProdutoController
from controllers.relatorio_controller import RelatorioController
from controllers.sistema_controller import SistemaController
from controllers.usuario_controller import UsuarioController
from database import connection, schema
from middlewares.auth import Autenticacao
from middlewares.error_handler import registrar_tratamento_de_erros
from models.admin_model import AdminModel
from models.pedido_model import PedidoModel
from models.produto_model import ProdutoModel
from models.sistema_model import SistemaModel
from models.usuario_model import UsuarioModel
from routes.admin_routes import criar_admin_routes
from routes.pedido_routes import criar_pedido_routes
from routes.produto_routes import criar_produto_routes
from routes.relatorio_routes import criar_relatorio_routes
from routes.sistema_routes import criar_sistema_routes
from routes.usuario_routes import criar_usuario_routes
from services.notificacao_service import NotificacaoService
from services.pedido_service import PedidoService
from services.relatorio_service import RelatorioService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    connection.init_app(app)
    with app.app_context():
        schema.init_db(connection.get_db())

    obter_conexao = connection.get_db
    produto_model = ProdutoModel(obter_conexao)
    usuario_model = UsuarioModel(obter_conexao)
    pedido_model = PedidoModel(obter_conexao)
    admin_model = AdminModel(obter_conexao)
    sistema_model = SistemaModel(obter_conexao)

    auth = Autenticacao(usuario_model)
    pedido_service = PedidoService(pedido_model, produto_model, usuario_model, NotificacaoService())
    relatorio_service = RelatorioService(pedido_model)

    app.register_blueprint(criar_produto_routes(ProdutoController(produto_model), auth))
    app.register_blueprint(criar_usuario_routes(UsuarioController(usuario_model, auth), auth))
    app.register_blueprint(criar_pedido_routes(PedidoController(pedido_service, pedido_model, auth), auth))
    app.register_blueprint(criar_relatorio_routes(RelatorioController(relatorio_service), auth))
    app.register_blueprint(criar_sistema_routes(SistemaController(sistema_model)))
    app.register_blueprint(criar_admin_routes(AdminController(admin_model), auth))

    registrar_tratamento_de_erros(app)
    return app


app = create_app()

if __name__ == "__main__":
    logger.info("SERVIDOR INICIADO - rodando em http://localhost:%s", app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
