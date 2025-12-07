import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import get_db
from src.schemas.base import Base


TEST_DB_URL = "postgresql://postgres:postgres@127.0.0.1:5432/test_db"

# Setup test database
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_users(db_session):
    """Create test users in different komorki_organizacyjne."""
    from src.schemas.users import User
    from src.schemas.komorki_organizacyjne import KomorkaOrganizacyjna
    
    # Ensure komorki exist
    komorki = []
    for i in range(3):
        komorka = db_session.query(KomorkaOrganizacyjna).filter_by(id=i).first()
        if not komorka:
            komorka = KomorkaOrganizacyjna(id=i, nazwa=f"Test Komorka {i}")
            db_session.add(komorka)
        komorki.append(komorka)
    
    db_session.commit()
    
    # Create users
    users = [
        User(
            id=1,
            firstname="Anna",
            lastname="Kowalska",
            email="anna.kowalska@test.pl",
            komorka_organizacyjna_id=0
        ),
        User(
            id=2,
            firstname="Jan",
            lastname="Nowak",
            email="jan.nowak@test.pl",
            komorka_organizacyjna_id=0
        ),
        User(
            id=3,
            firstname="Piotr",
            lastname="Wiśniewski",
            email="piotr.wisniewski@test.pl",
            komorka_organizacyjna_id=1
        ),
    ]
    
    for user in users:
        db_session.add(user)
    
    db_session.commit()
    
    for user in users:
        db_session.refresh(user)
    
    return users
