import sys
import os
import pytest

# Make the backend package importable from within the tests/ subdirectory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
# Make helpers.py importable as a plain module
sys.path.insert(0, os.path.dirname(__file__))

from api import app as flask_app
from models import db as _db


@pytest.fixture(scope='session')
def app():
    """Single Flask app instance reused for the whole test session."""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': False,
    })
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Wipe all table data after every test so tests are fully isolated."""
    yield
    with app.app_context():
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()



