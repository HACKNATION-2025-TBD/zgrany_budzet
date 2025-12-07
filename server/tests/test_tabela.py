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

    def test_create_planowanie_budzetu(self, client, db_session, test_users):
        """Test creating a new planowanie_budzetu record."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }

        response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_update_string_field(self, client, db_session, test_users):
        """Test updating a string field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update the field
        update_payload = {
            "field": "nazwa_projektu",
            "value": "Updated Name"
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_update_foreign_key_string_field(self, client, db_session, test_users):
        """Test updating a foreign key string field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update dzial_kod
        update_payload = {
            "field": "dzial_kod",
            "value": "801"
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_update_foreign_key_int_field(self, client, db_session, test_users):
        """Test updating a foreign key integer field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update grupa_wydatkow_id
        update_payload = {
            "field": "grupa_wydatkow_id",
            "value": 5
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_update_nullable_field_to_null(self, client, db_session, test_users):
        """Test updating a nullable string field to null."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update to null
        update_payload = {
            "field": "szczegolowe_uzasadnienie_realizacji",
            "value": None
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_get_all_planowanie_budzetu(self, client, db_session, test_users):
        """Test getting all planowanie_budzetu records with latest versions."""
        user = test_users[0]
        
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
                "komorka_organizacyjna_id": user.komorka_organizacyjna_id
            }
            client.post(
                "/api/planowanie_budzetu",
                json=payload,
                headers={"Authorization": str(user.id)}
            )

        response = client.get(
            "/api/planowanie_budzetu",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("id" in item for item in data)
        assert all("nazwa_projektu" in item for item in data)

    def test_get_single_planowanie_budzetu(self, client, db_session, test_users):
        """Test getting a single planowanie_budzetu record."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == planowanie_id
        assert data["nazwa_projektu"] == "Single Project"
        assert data["nazwa_zadania"] == "Task"

    def test_get_field_history_string_field(self, client, db_session, test_users):
        """Test getting history for a specific string field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update nazwa_projektu several times
        for i in range(3):
            update_payload = {
                "field": "nazwa_projektu",
                "value": f"Updated Project {i+1}"
            }
            client.patch(
                f"/api/planowanie_budzetu/{planowanie_id}",
                json=update_payload,
                headers={"Authorization": str(user.id)}
            )

        # Get field history
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/field_history/nazwa_projektu",
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_get_field_history_fk_string_field(self, client, db_session, test_users):
        """Test getting history for a foreign key string field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update dzial_kod
        for kod in ["801", "802"]:
            update_payload = {
                "field": "dzial_kod",
                "value": kod
            }
            client.patch(
                f"/api/planowanie_budzetu/{planowanie_id}",
                json=update_payload,
                headers={"Authorization": str(user.id)}
            )

        # Get field history
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/field_history/dzial_kod",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "dzial_kod"
        
        history = data["history"]
        assert len(history) == 3  # Original + 2 updates
        assert history[0]["value"] == "802"
        assert history[1]["value"] == "801"
        assert history[2]["value"] == "750"

    def test_get_field_history_fk_int_field(self, client, db_session, test_users):
        """Test getting history for a foreign key integer field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update grupa_wydatkow_id
        for value in [2, 3]:
            update_payload = {
                "field": "grupa_wydatkow_id",
                "value": value
            }
            client.patch(
                f"/api/planowanie_budzetu/{planowanie_id}",
                json=update_payload,
                headers={"Authorization": str(user.id)}
            )

        # Get field history
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/field_history/grupa_wydatkow_id",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "grupa_wydatkow_id"
        
        history = data["history"]
        assert len(history) == 3
        assert history[0]["value"] == 3
        assert history[1]["value"] == 2
        assert history[2]["value"] == 1

    def test_get_field_history_unknown_field(self, client, db_session, test_users):
        """Test getting history for a field that doesn't exist."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/field_history/non_existent_field",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 400
        assert "Unknown field" in response.json()["detail"]

    def test_get_field_history_nonexistent_record(self, client, test_users):
        """Test getting field history for a record that doesn't exist."""
        user = test_users[0]
        
        response = client.get(
            "/api/planowanie_budzetu/99999/field_history/nazwa_projektu",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_unknown_field(self, client, db_session, test_users):
        """Test updating a field that doesn't exist."""
        user = test_users[0]
        
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        update_payload = {
            "field": "non_existent_field",
            "value": "some value"
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 400
        assert "Unknown field" in response.json()["detail"]

    def test_get_nonexistent_record(self, client, test_users):
        """Test getting a record that doesn't exist."""
        user = test_users[0]
        
        response = client.get(
            "/api/planowanie_budzetu/99999",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_fields_history_status_no_history(self, client, db_session, test_users):
        """Test getting fields history status when no fields have been updated."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Get fields history status
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "fields" in data
        
        fields = data["fields"]
        # All fields should have False since nothing was updated
        assert fields["nazwa_projektu"] is False
        assert fields["nazwa_zadania"] is False
        assert fields["szczegolowe_uzasadnienie_realizacji"] is False
        assert fields["budzet"] is False
        assert fields["czesc_budzetowa_kod"] is False
        assert fields["dzial_kod"] is False
        assert fields["rozdzial_kod"] is False
        assert fields["paragraf_kod"] is False
        assert fields["zrodlo_finansowania_kod"] is False
        assert fields["grupa_wydatkow_id"] is False
        assert fields["komorka_organizacyjna_id"] is False

    def test_get_fields_history_status_with_updates(self, client, db_session, test_users):
        """Test getting fields history status after some fields have been updated."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update some fields
        client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json={"field": "nazwa_projektu", "value": "Updated Project"},
            headers={"Authorization": str(user.id)}
        )
        client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json={"field": "dzial_kod", "value": "801"},
            headers={"Authorization": str(user.id)}
        )
        client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json={"field": "grupa_wydatkow_id", "value": 2},
            headers={"Authorization": str(user.id)}
        )

        # Get fields history status
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "fields" in data
        
        fields = data["fields"]
        # Updated fields should have True
        assert fields["nazwa_projektu"] is True
        assert fields["dzial_kod"] is True
        assert fields["grupa_wydatkow_id"] is True
        
        # Non-updated fields should have False
        assert fields["nazwa_zadania"] is False
        assert fields["szczegolowe_uzasadnienie_realizacji"] is False
        assert fields["budzet"] is False
        assert fields["czesc_budzetowa_kod"] is False
        assert fields["rozdzial_kod"] is False
        assert fields["paragraf_kod"] is False
        assert fields["zrodlo_finansowania_kod"] is False
        assert fields["komorka_organizacyjna_id"] is False

    def test_get_fields_history_status_multiple_updates_same_field(self, client, db_session, test_users):
        """Test that field shows history status even after multiple updates."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]

        # Update the same field multiple times
        for i in range(5):
            client.patch(
                f"/api/planowanie_budzetu/{planowanie_id}",
                json={"field": "nazwa_projektu", "value": f"Version {i+1}"},
                headers={"Authorization": str(user.id)}
            )

        # Get fields history status
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        fields = data["fields"]
        
        # Should still show True (has more than 1 version)
        assert fields["nazwa_projektu"] is True

    def test_get_fields_history_status_nonexistent_record(self, client, test_users):
        """Test getting fields history status for non-existent record."""
        user = test_users[0]
        
        response = client.get(
            "/api/planowanie_budzetu/99999/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRokBudzetowyEndpoints:
    """Tests for rok_budzetowy endpoints."""

    def test_create_rok_budzetowy(self, client, db_session, test_users):
        """Test creating a new rok_budzetowy record."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        # Create rok_budzetowy
        payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        response = client.post(
            "/api/rok_budzetowy",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_update_numeric_field(self, client, db_session, test_users):
        """Test updating a numeric field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        # Update limit
        update_payload = {
            "field": "limit",
            "value": 60000.00
        }
        response = client.patch(
            f"/api/rok_budzetowy/{rok_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
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

    def test_get_rok_budzetowy_field_history_limit(self, client, db_session, test_users):
        """Test getting history for limit field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        # Update limit
        for value in [60000.00, 70000.00, 80000.00]:
            update_payload = {
                "field": "limit",
                "value": value
            }
            client.patch(
                f"/api/rok_budzetowy/{rok_id}",
                json=update_payload,
                headers={"Authorization": str(user.id)}
            )

        # Get field history
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/field_history/limit",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "limit"
        
        history = data["history"]
        assert len(history) == 4  # Original + 3 updates
        assert history[0]["value"] == 80000.00
        assert history[-1]["value"] == 50000.00

    def test_get_rok_budzetowy_field_history_potrzeba(self, client, db_session, test_users):
        """Test getting history for potrzeba field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        # Update potrzeba
        update_payload = {
            "field": "potrzeba",
            "value": 85000.00
        }
        client.patch(
            f"/api/rok_budzetowy/{rok_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )

        # Get field history
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/field_history/potrzeba",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "potrzeba"
        
        history = data["history"]
        assert len(history) == 2
        assert history[0]["value"] == 85000.00
        assert history[1]["value"] == 75000.00

    def test_get_rok_budzetowy_field_history_unknown_field(self, client, db_session, test_users):
        """Test getting history for unknown field in rok_budzetowy."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/field_history/non_existent_field",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 400
        assert "Unknown field" in response.json()["detail"]

    def test_create_rok_budzetowy_invalid_planowanie(self, client, test_users):
        """Test creating rok_budzetowy with non-existent planowanie_budzetu_id."""
        user = test_users[0]
        
        payload = {
            "planowanie_budzetu_id": 99999,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        response = client.post(
            "/api/rok_budzetowy",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_rok_budzetowy_fields_history_status_no_history(self, client, db_session, test_users):
        """Test getting fields history status for rok_budzetowy when no fields have been updated."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        # Get fields history status
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "fields" in data
        
        fields = data["fields"]
        # Both fields should have False since nothing was updated
        assert fields["limit"] is False
        assert fields["potrzeba"] is False

    def test_get_rok_budzetowy_fields_history_status_with_updates(self, client, db_session, test_users):
        """Test getting fields history status after some fields have been updated."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        # Update only limit field
        client.patch(
            f"/api/rok_budzetowy/{rok_id}",
            json={
                "field": "limit",
                "value": 60000.00
            },
            headers={"Authorization": str(user.id)}
        )

        # Get fields history status
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        fields = data["fields"]
        
        # Updated field should have True
        assert fields["limit"] is True
        
        # Non-updated field should have False
        assert fields["potrzeba"] is False

    def test_get_rok_budzetowy_fields_history_status_both_updated(self, client, db_session, test_users):
        """Test fields history status when both fields have been updated."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        # Update both fields
        client.patch(
            f"/api/rok_budzetowy/{rok_id}",
            json={
                "field": "limit",
                "value": 60000.00
            },
            headers={"Authorization": str(user.id)}
        )
        client.patch(
            f"/api/rok_budzetowy/{rok_id}",
            json={
                "field": "potrzeba",
                "value": 85000.00
            },
            headers={"Authorization": str(user.id)}
        )

        # Get fields history status
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        fields = data["fields"]
        
        # Both fields should have True
        assert fields["limit"] is True
        assert fields["potrzeba"] is True

    def test_get_rok_budzetowy_fields_history_status_multiple_updates(self, client, db_session, test_users):
        """Test fields history status with multiple updates to the same field."""
        user = test_users[0]
        
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
            "komorka_organizacyjna_id": user.komorka_organizacyjna_id
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = planowanie_response.json()["id"]

        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        rok_response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user.id)}
        )
        rok_id = rok_response.json()["id"]

        # Update limit field multiple times
        for value in [60000.00, 70000.00, 80000.00]:
            client.patch(
                f"/api/rok_budzetowy/{rok_id}",
                json={
                    "field": "limit",
                    "value": value
                },
                headers={"Authorization": str(user.id)}
            )

        # Get fields history status
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        fields = data["fields"]
        
        # Limit should have True (has more than 1 version)
        assert fields["limit"] is True
        # Potrzeba should still have False
        assert fields["potrzeba"] is False

    def test_get_rok_budzetowy_fields_history_status_nonexistent_record(self, client, test_users):
        """Test getting fields history status for non-existent rok_budzetowy."""
        user = test_users[0]
        
        response = client.get(
            "/api/rok_budzetowy/99999/fields_history_status",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
