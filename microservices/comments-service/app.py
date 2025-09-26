from flask import Flask
from routes.comment_route import bp
from db_connector import get_db
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # Registrar rutas
    app.register_blueprint(bp, url_prefix="/v1")

    @app.get("/health")
    def health():
        try:
            db = get_db()
            list(db.collections())
            return {"status": "ok"}
        except Exception as e:
            return {"status": "degraded", "error": str(e)}, 503
        
    @app.get("/live")
    def live():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8091, debug=True)
