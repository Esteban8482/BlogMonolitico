import pytest
from app import create_app
from db_connector import db


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
