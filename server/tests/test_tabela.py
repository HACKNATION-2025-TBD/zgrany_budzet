import pytest
from src.schemas.planowanie_budzetu import PlanowanieBudzetu
from src.schemas.rok_budzetowy import RokBudzetowy
from src.schemas.versioned_fields import (
    VersionedStringField,
    VersionedNumericField,
    VersionedForeignKeyField
)


class TestPlanowanieBudzetuEndpoints:
    """Tests for planowanie_budzetu endpoints."""

    def test_create_planowanie_budzetu(self, client, db_session):
        """Test creating a new planowanie_budzetu record."""
        payload = {
            "nazwa_projektu": "Test Project",
            "nazwa_zadania": "Test Task",
            "szczegolowe_uzasadnienie_realizacji": "Test justification",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }

        response = client.post("/api/planowanie_budzetu", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "Created successfully"
        
        planowanie_id = data["id"]

        # Verify in database
        planowanie = db_session.query(PlanowanieBudzetu).filter_by(id=planowanie_id).first()
        assert planowanie is not None

        # Check versioned fields
        nazwa_projektu_versions = db_session.query(VersionedStringField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="nazwa_projektu"
        ).all()
        assert len(nazwa_projektu_versions) == 1
        assert nazwa_projektu_versions[0].value == "Test Project"

        czesc_versions = db_session.query(VersionedForeignKeyField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="czesc_budzetowa_kod"
        ).all()
        assert len(czesc_versions) == 1
        assert czesc_versions[0].value_string == "75"

        grupa_versions = db_session.query(VersionedForeignKeyField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="grupa_wydatkow_id"
        ).all()
        assert len(grupa_versions) == 1
        assert grupa_versions[0].value_int == 1

    def test_update_string_field(self, client, db_session):
        """Test updating a string field."""
        # First create a record
        payload = {
            "nazwa_projektu": "Original Name",
            "nazwa_zadania": "Task",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Update the field
        update_payload = {
            "field": "nazwa_projektu",
            "value": "Updated Name"
        }
        response = client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["field"] == "nazwa_projektu"
        assert data["value"] == "Updated Name"

        # Verify in database - should have 2 versions
        versions = db_session.query(VersionedStringField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="nazwa_projektu"
        ).order_by(VersionedStringField.timestamp).all()
        
        assert len(versions) == 2
        assert versions[0].value == "Original Name"
        assert versions[1].value == "Updated Name"
        assert versions[1].timestamp > versions[0].timestamp

    def test_update_foreign_key_string_field(self, client, db_session):
        """Test updating a foreign key string field."""
        # Create record
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Update dzial_kod
        update_payload = {
            "field": "dzial_kod",
            "value": "801"
        }
        response = client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)
        
        assert response.status_code == 200

        # Verify versions
        versions = db_session.query(VersionedForeignKeyField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="dzial_kod"
        ).order_by(VersionedForeignKeyField.timestamp).all()
        
        assert len(versions) == 2
        assert versions[0].value_string == "750"
        assert versions[1].value_string == "801"

    def test_update_foreign_key_int_field(self, client, db_session):
        """Test updating a foreign key integer field."""
        # Create record
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Update grupa_wydatkow_id
        update_payload = {
            "field": "grupa_wydatkow_id",
            "value": 5
        }
        response = client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)
        
        assert response.status_code == 200

        # Verify versions
        versions = db_session.query(VersionedForeignKeyField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="grupa_wydatkow_id"
        ).order_by(VersionedForeignKeyField.timestamp).all()
        
        assert len(versions) == 2
        assert versions[0].value_int == 1
        assert versions[1].value_int == 5

    def test_update_nullable_field_to_null(self, client, db_session):
        """Test updating a nullable string field to null."""
        # Create record
        payload = {
            "nazwa_projektu": "Project",
            "szczegolowe_uzasadnienie_realizacji": "Original justification",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Update to null
        update_payload = {
            "field": "szczegolowe_uzasadnienie_realizacji",
            "value": None
        }
        response = client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)
        
        assert response.status_code == 200

        # Verify versions
        versions = db_session.query(VersionedStringField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="szczegolowe_uzasadnienie_realizacji"
        ).order_by(VersionedStringField.timestamp).all()
        
        assert len(versions) == 2
        assert versions[0].value == "Original justification"
        assert versions[1].value is None

    def test_get_all_planowanie_budzetu(self, client, db_session):
        """Test getting all planowanie_budzetu records with latest versions."""
        # Create 2 records
        for i in range(2):
            payload = {
                "nazwa_projektu": f"Project {i+1}",
                "budzet": "2024",
                "czesc_budzetowa_kod": "75",
                "dzial_kod": "750",
                "rozdzial_kod": "75011",
                "paragraf_kod": "4210",
                "zrodlo_finansowania_kod": "1",
                "grupa_wydatkow_id": 1,
                "komorka_organizacyjna_id": 1
            }
            client.post("/api/planowanie_budzetu", json=payload)

        response = client.get("/api/planowanie_budzetu")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("id" in item for item in data)
        assert all("nazwa_projektu" in item for item in data)

    def test_get_single_planowanie_budzetu(self, client, db_session):
        """Test getting a single planowanie_budzetu record."""
        payload = {
            "nazwa_projektu": "Single Project",
            "nazwa_zadania": "Task",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        response = client.get(f"/api/planowanie_budzetu/{planowanie_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == planowanie_id
        assert data["nazwa_projektu"] == "Single Project"
        assert data["nazwa_zadania"] == "Task"

    def test_get_history(self, client, db_session):
        """Test getting version history for a record."""
        # Create record
        payload = {
            "nazwa_projektu": "Original",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Make several updates
        for i in range(3):
            update_payload = {
                "field": "nazwa_projektu",
                "value": f"Version {i+2}"
            }
            client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)

        # Get history
        response = client.get(f"/api/planowanie_budzetu/{planowanie_id}/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "nazwa_projektu_history" in data
        
        history = data["nazwa_projektu_history"]
        assert len(history) == 4  # Original + 3 updates
        assert history[0]["value"] == "Version 4"  # Most recent first
        assert history[-1]["value"] == "Original"  # Original last
        
        # Verify timestamps are in descending order
        timestamps = [item["timestamp"] for item in history]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_get_field_history_string_field(self, client, db_session):
        """Test getting history for a specific string field."""
        # Create record
        payload = {
            "nazwa_projektu": "Original Project",
            "nazwa_zadania": "Original Task",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Update nazwa_projektu several times
        for i in range(3):
            update_payload = {
                "field": "nazwa_projektu",
                "value": f"Updated Project {i+1}"
            }
            client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)

        # Get field history
        response = client.get(f"/api/planowanie_budzetu/{planowanie_id}/field_history/nazwa_projektu")
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "nazwa_projektu"
        assert "history" in data
        
        history = data["history"]
        assert len(history) == 4  # Original + 3 updates
        assert history[0]["value"] == "Updated Project 3"  # Most recent
        assert history[-1]["value"] == "Original Project"  # Original
        
        # Verify all have timestamps
        assert all("timestamp" in item for item in history)

    def test_get_field_history_fk_string_field(self, client, db_session):
        """Test getting history for a foreign key string field."""
        # Create record
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Update dzial_kod
        for kod in ["801", "802"]:
            update_payload = {
                "field": "dzial_kod",
                "value": kod
            }
            client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)

        # Get field history
        response = client.get(f"/api/planowanie_budzetu/{planowanie_id}/field_history/dzial_kod")
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "dzial_kod"
        
        history = data["history"]
        assert len(history) == 3  # Original + 2 updates
        assert history[0]["value"] == "802"
        assert history[1]["value"] == "801"
        assert history[2]["value"] == "750"

    def test_get_field_history_fk_int_field(self, client, db_session):
        """Test getting history for a foreign key integer field."""
        # Create record
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        # Update grupa_wydatkow_id
        for value in [2, 3]:
            update_payload = {
                "field": "grupa_wydatkow_id",
                "value": value
            }
            client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)

        # Get field history
        response = client.get(f"/api/planowanie_budzetu/{planowanie_id}/field_history/grupa_wydatkow_id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "grupa_wydatkow_id"
        
        history = data["history"]
        assert len(history) == 3
        assert history[0]["value"] == 3
        assert history[1]["value"] == 2
        assert history[2]["value"] == 1

    def test_get_field_history_unknown_field(self, client, db_session):
        """Test getting history for a field that doesn't exist."""
        # Create record
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        response = client.get(f"/api/planowanie_budzetu/{planowanie_id}/field_history/non_existent_field")
        
        assert response.status_code == 400
        assert "Unknown field" in response.json()["detail"]

    def test_get_field_history_nonexistent_record(self, client):
        """Test getting field history for a record that doesn't exist."""
        response = client.get("/api/planowanie_budzetu/99999/field_history/nazwa_projektu")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_unknown_field(self, client, db_session):
        """Test updating a field that doesn't exist."""
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        create_response = client.post("/api/planowanie_budzetu", json=payload)
        planowanie_id = create_response.json()["id"]

        update_payload = {
            "field": "non_existent_field",
            "value": "some value"
        }
        response = client.patch(f"/api/planowanie_budzetu/{planowanie_id}", json=update_payload)
        
        assert response.status_code == 400
        assert "Unknown field" in response.json()["detail"]

    def test_get_nonexistent_record(self, client):
        """Test getting a record that doesn't exist."""
        response = client.get("/api/planowanie_budzetu/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRokBudzetowyEndpoints:
    """Tests for rok_budzetowy endpoints."""

    def test_create_rok_budzetowy(self, client, db_session):
        """Test creating a new rok_budzetowy record."""
        # First create planowanie_budzetu
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        planowanie_response = client.post("/api/planowanie_budzetu", json=planowanie_payload)
        planowanie_id = planowanie_response.json()["id"]

        # Create rok_budzetowy
        payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        response = client.post("/api/rok_budzetowy", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        
        rok_id = data["id"]

        # Verify in database
        rok = db_session.query(RokBudzetowy).filter_by(id=rok_id).first()
        assert rok is not None
        assert rok.planowanie_budzetu_id == planowanie_id

        # Check versioned numeric fields
        limit_versions = db_session.query(VersionedNumericField).filter_by(
            entity_type="rok_budzetowy",
            entity_id=rok_id,
            field_name="limit"
        ).all()
        assert len(limit_versions) == 1
        assert float(limit_versions[0].value) == 50000.00

        potrzeba_versions = db_session.query(VersionedNumericField).filter_by(
            entity_type="rok_budzetowy",
            entity_id=rok_id,
            field_name="potrzeba"
        ).all()
        assert len(potrzeba_versions) == 1
        assert float(potrzeba_versions[0].value) == 75000.00

    def test_update_numeric_field(self, client, db_session):
        """Test updating a numeric field."""
        # Create planowanie_budzetu and rok_budzetowy
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        planowanie_response = client.post("/api/planowanie_budzetu", json=planowanie_payload)
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post("/api/rok_budzetowy", json=rok_payload)
        rok_id = rok_response.json()["id"]

        # Update limit
        update_payload = {
            "field": "limit",
            "value": 60000.00
        }
        response = client.patch(f"/api/rok_budzetowy/{rok_id}", json=update_payload)
        
        assert response.status_code == 200

        # Verify versions
        versions = db_session.query(VersionedNumericField).filter_by(
            entity_type="rok_budzetowy",
            entity_id=rok_id,
            field_name="limit"
        ).order_by(VersionedNumericField.timestamp).all()
        
        assert len(versions) == 2
        assert float(versions[0].value) == 50000.00
        assert float(versions[1].value) == 60000.00

    def test_get_rok_budzetowy_history(self, client, db_session):
        """Test getting version history for rok_budzetowy."""
        # Create records
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        planowanie_response = client.post("/api/planowanie_budzetu", json=planowanie_payload)
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post("/api/rok_budzetowy", json=rok_payload)
        rok_id = rok_response.json()["id"]

        # Make updates
        for value in [60000.00, 70000.00]:
            update_payload = {
                "field": "limit",
                "value": value
            }
            client.patch(f"/api/rok_budzetowy/{rok_id}", json=update_payload)

        # Get history
        response = client.get(f"/api/rok_budzetowy/{rok_id}/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "limit_history" in data
        
        history = data["limit_history"]
        assert len(history) == 3  # Original + 2 updates
        assert history[0]["value"] == 70000.00  # Most recent
        assert history[-1]["value"] == 50000.00  # Original

    def test_get_rok_budzetowy_field_history_limit(self, client, db_session):
        """Test getting history for limit field."""
        # Create records
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        planowanie_response = client.post("/api/planowanie_budzetu", json=planowanie_payload)
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post("/api/rok_budzetowy", json=rok_payload)
        rok_id = rok_response.json()["id"]

        # Update limit
        for value in [60000.00, 70000.00, 80000.00]:
            update_payload = {
                "field": "limit",
                "value": value
            }
            client.patch(f"/api/rok_budzetowy/{rok_id}", json=update_payload)

        # Get field history
        response = client.get(f"/api/rok_budzetowy/{rok_id}/field_history/limit")
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "limit"
        
        history = data["history"]
        assert len(history) == 4  # Original + 3 updates
        assert history[0]["value"] == 80000.00
        assert history[-1]["value"] == 50000.00

    def test_get_rok_budzetowy_field_history_potrzeba(self, client, db_session):
        """Test getting history for potrzeba field."""
        # Create records
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        planowanie_response = client.post("/api/planowanie_budzetu", json=planowanie_payload)
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post("/api/rok_budzetowy", json=rok_payload)
        rok_id = rok_response.json()["id"]

        # Update potrzeba
        update_payload = {
            "field": "potrzeba",
            "value": 85000.00
        }
        client.patch(f"/api/rok_budzetowy/{rok_id}", json=update_payload)

        # Get field history
        response = client.get(f"/api/rok_budzetowy/{rok_id}/field_history/potrzeba")
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "potrzeba"
        
        history = data["history"]
        assert len(history) == 2
        assert history[0]["value"] == 85000.00
        assert history[1]["value"] == 75000.00

    def test_get_rok_budzetowy_field_history_unknown_field(self, client, db_session):
        """Test getting history for unknown field in rok_budzetowy."""
        # Create records
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        planowanie_response = client.post("/api/planowanie_budzetu", json=planowanie_payload)
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post("/api/rok_budzetowy", json=rok_payload)
        rok_id = rok_response.json()["id"]

        response = client.get(f"/api/rok_budzetowy/{rok_id}/field_history/non_existent_field")
        
        assert response.status_code == 400
        assert "Unknown field" in response.json()["detail"]

    def test_create_rok_budzetowy_invalid_planowanie(self, client):
        """Test creating rok_budzetowy with non-existent planowanie_budzetu_id."""
        payload = {
            "planowanie_budzetu_id": 99999,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        response = client.post("/api/rok_budzetowy", json=payload)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
