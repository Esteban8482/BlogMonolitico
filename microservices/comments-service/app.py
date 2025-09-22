from flask import Flask
from db_connector import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comments.db"  # simple para probar
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # *** CLAVE: inicializar la extensión con la app ***
    db.init_app(app)

    # Registrar rutas DESPUÉS de init_app para evitar imports prematuros
    from routes.comment_route import bp
    app.register_blueprint(bp, url_prefix="/v1")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Crear tablas dentro del app_context y después de init_app
    with app.app_context():
        from models import Comment  # asegura que el modelo use 'db' de db_connector
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8091)
