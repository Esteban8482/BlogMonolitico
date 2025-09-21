import pytest
from app import create_app


@pytest.fixture
def app():
    config = {
        "TESTING": True,
    }

    app = create_app(config_override=config, init_db=False)

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
