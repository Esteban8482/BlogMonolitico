from flask import Flask
from db_connector import db

def create_app():
    app = Flask(__name__)
    # TODO: Migrar almacenamiento de comentarios a un servicio distribuido.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comments.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    db.init_app(app)


    from routes.comment_route import bp
    app.register_blueprint(bp, url_prefix="/v1")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    with app.app_context():
        from models import Comment 
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8091)
