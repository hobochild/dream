import pytest
from unittest.mock import Mock

from sqlalchemy_utils.functions import drop_database, create_database, database_exists
from flask_migrate import Migrate, upgrade

from app import create_app
from app.database import db as _db
from app.models import User
from app.session import session
from config import SQLALCHEMY_DATABASE_URI
from celery import Task


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    # Suffix the db name with test for tests.
    test_database_uri = SQLALCHEMY_DATABASE_URI + "_test"
    app = create_app({"SQLALCHEMY_DATABASE_URI": test_database_uri})

    if database_exists(test_database_uri):
        drop_database(test_database_uri)

    create_database(test_database_uri)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        drop_database(test_database_uri)
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session", autouse=True)
def db(app):
    """Session-wide test database."""
    Migrate(app, _db)
    upgrade()

    return _db


@pytest.fixture(scope="function", autouse=True)
def app_session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="function")
def dummy_user(db):
    """
    util function to create a test case user.
    """

    def create_dummy_user(email="x@x.com") -> User:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
        return user

    return create_dummy_user


@pytest.fixture(scope="function")
def signin(client):
    """
    util function to create a test case user.
    """

    def inner(user: User) -> None:
        with client.session_transaction() as sesh:
            session.flask_session = sesh
            session.signin(user)
            session.flask_session = None

    return inner


@pytest.fixture(scope="function", autouse=True)
def dummy_mail_manager(app):
    """
    We never want to send real emails in our test suite.
    This replaces it with a Mock so you can assert it was called.
    """

    dummy_mail_manager = Mock()
    app.mail_manager = dummy_mail_manager
    return dummy_mail_manager


@pytest.fixture(scope="function", autouse=True)
def monkey_patch_celery_async(monkeypatch):
    """
    This ensures that celery tasks are called locally
    so you can assert their results within the test
    without running the worker.
    """
    monkeypatch.setattr("celery.Task.apply_async", Task.apply)
