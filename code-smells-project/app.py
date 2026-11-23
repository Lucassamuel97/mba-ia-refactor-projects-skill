"""Composition root: monta as camadas da aplicação e inicia o servidor."""
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
from database import connection, schema, seed
from middlewares.error_handler import registrar_tratadores_de_erro
from models.admin_model import AdminModel
from models.pedido_model import PedidoModel
from models.produto_model import ProdutoModel
from models.usuario_model import UsuarioModel
from routes import admin_routes, pedido_routes, produto_routes, relatorio_routes, sistema_routes, usuario_routes
from services import senha_service
from services.notificacao_service import NotificacaoService
from services.pedido_service import PedidoService
from services.relatorio_service import RelatorioService
from services.usuario_service import UsuarioService

logger = logging.getLogger(__name__)


def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"], logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    CORS(app)
    connection.init_app(app)

    produto_model = ProdutoModel(connection.get_db)
    usuario_model = UsuarioModel(connection.get_db)
    pedido_model = PedidoModel(connection.get_db)
    admin_model = AdminModel(connection.get_db)

    usuario_service = UsuarioService(usuario_model, senha_service)
    pedido_service = PedidoService(pedido_model, produto_model, usuario_model, NotificacaoService())
    relatorio_service = RelatorioService(pedido_model)

    with app.app_context():
        db = connection.get_db()
        schema.criar_tabelas(db)
        seed.popular_se_vazio(db, senha_service.gerar_hash)
        usuario_service.migrar_senhas_legadas()

    # A ordem de registro é a mesma das rotas originais.
    blueprints = (
        produto_routes.criar_blueprint(ProdutoController(produto_model)),
        usuario_routes.criar_blueprint(UsuarioController(usuario_model, usuario_service)),
        pedido_routes.criar_blueprint(PedidoController(pedido_model, pedido_service)),
        relatorio_routes.criar_blueprint(RelatorioController(relatorio_service)),
        sistema_routes.criar_blueprint(SistemaController(produto_model, usuario_model, pedido_model)),
        admin_routes.criar_blueprint(AdminController(admin_model)),
    )
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    registrar_tratadores_de_erro(app)
    return app


app = create_app()

if __name__ == "__main__":
    logger.info("Servidor iniciado em http://%s:%s", app.config["HOST"], app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
