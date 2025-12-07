import pytest
from src.schemas.users import User
from src.schemas.komorki_organizacyjne import KomorkaOrganizacyjna
from src.schemas.planowanie_budzetu import PlanowanieBudzetu
from src.schemas.rok_budzetowy import RokBudzetowy
from src.schemas.versioned_fields import VersionedForeignKeyField


class TestAuthorizationHeader:
    """Tests for authorization header validation."""

    def test_missing_authorization_header(self, client):
        """Test that requests without Authorization header are rejected."""
        response = client.get("/api/planowanie_budzetu")
        
        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["detail"]

    def test_invalid_authorization_header_format(self, client):
        """Test that non-numeric Authorization header is rejected."""
        response = client.get(
            "/api/planowanie_budzetu",
            headers={"Authorization": "invalid"}
        )
        
        assert response.status_code == 401
        assert "Invalid authorization format" in response.json()["detail"]

    def test_nonexistent_user_id(self, client, db_session):
        """Test that non-existent user_id is rejected."""
        response = client.get(
            "/api/planowanie_budzetu",
            headers={"Authorization": "99999"}
        )
        
        assert response.status_code == 401
        assert "User not found" in response.json()["detail"]

    def test_valid_authorization_header(self, client, db_session, test_users):
        """Test that valid Authorization header works."""
        user = test_users[0]
        
        response = client.get(
            "/api/planowanie_budzetu",
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200


class TestKomorkaOrganizacyjnaAccess:
    """Tests for komorka_organizacyjna based access control."""

    def test_create_planowanie_in_own_komorka(self, client, db_session, test_users):
        """Test creating planowanie in user's own komorka_organizacyjna."""
        user = test_users[0]  # User in komorka 0
        
        payload = {
            "nazwa_projektu": "Test Project",
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
        assert "id" in response.json()

    def test_create_planowanie_in_different_komorka(self, client, db_session, test_users):
        """Test that user cannot create planowanie in different komorka_organizacyjna."""
        user = test_users[0]  # User in komorka 0
        different_komorka_id = 1  # Different komorka
        
        payload = {
            "nazwa_projektu": "Test Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": different_komorka_id
        }
        
        response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 403
        assert "different organizational unit" in response.json()["detail"]

    def test_get_all_planowanie_filters_by_komorka(self, client, db_session, test_users):
        """Test that get_all only returns planowania from user's komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # Create planowanie for komorka 0
        payload1 = {
            "nazwa_projektu": "Project Komorka 0",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        client.post(
            "/api/planowanie_budzetu",
            json=payload1,
            headers={"Authorization": str(user1.id)}
        )
        
        # Create planowanie for komorka 1
        payload2 = {
            "nazwa_projektu": "Project Komorka 1",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        client.post(
            "/api/planowanie_budzetu",
            json=payload2,
            headers={"Authorization": str(user2.id)}
        )
        
        # User1 should only see planowanie from komorka 0
        response1 = client.get(
            "/api/planowanie_budzetu",
            headers={"Authorization": str(user1.id)}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 1
        assert data1[0]["nazwa_projektu"] == "Project Komorka 0"
        
        # User2 should only see planowanie from komorka 1
        response2 = client.get(
            "/api/planowanie_budzetu",
            headers={"Authorization": str(user2.id)}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 1
        assert data2[0]["nazwa_projektu"] == "Project Komorka 1"

    def test_get_single_planowanie_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot access planowanie from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie in komorka 0
        payload = {
            "nazwa_projektu": "Private Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # User2 tries to access it
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}",
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_single_planowanie_from_same_komorka(self, client, db_session, test_users):
        """Test that user can access planowanie from same komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[1]  # Also komorka 0
        
        # User1 creates planowanie in komorka 0
        payload = {
            "nazwa_projektu": "Shared Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # User2 (same komorka) can access it
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}",
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nazwa_projektu"] == "Shared Project"

    def test_update_planowanie_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot update planowanie from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie
        payload = {
            "nazwa_projektu": "Original",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # User2 tries to update it
        update_payload = {
            "field": "nazwa_projektu",
            "value": "Hacked"
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_update_planowanie_from_same_komorka(self, client, db_session, test_users):
        """Test that user can update planowanie from same komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[1]  # Also komorka 0
        
        # User1 creates planowanie
        payload = {
            "nazwa_projektu": "Original",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # User2 (same komorka) can update it
        update_payload = {
            "field": "nazwa_projektu",
            "value": "Updated by colleague"
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 200
        assert response.json()["value"] == "Updated by colleague"

    def test_cannot_change_komorka_to_different_unit(self, client, db_session, test_users):
        """Test that user cannot change planowanie's komorka to different unit."""
        user = test_users[0]  # Komorka 0
        
        # Create planowanie in komorka 0
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # Try to change to komorka 1
        update_payload = {
            "field": "komorka_organizacyjna_id",
            "value": 1
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 403
        assert "different organizational unit" in response.json()["detail"]

    def test_can_update_komorka_to_same_unit(self, client, db_session, test_users):
        """Test that user can 'update' komorka to same value (no-op)."""
        user = test_users[0]  # Komorka 0
        
        # Create planowanie in komorka 0
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # Update to same komorka 0
        update_payload = {
            "field": "komorka_organizacyjna_id",
            "value": 0
        }
        response = client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json=update_payload,
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200

    def test_get_field_history_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot get field history from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates and updates planowanie
        payload = {
            "nazwa_projektu": "Original",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        client.patch(
            f"/api/planowanie_budzetu/{planowanie_id}",
            json={"field": "nazwa_projektu", "value": "Updated"},
            headers={"Authorization": str(user1.id)}
        )
        
        # User2 tries to get field history
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/field_history/nazwa_projektu",
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_fields_history_status_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot get fields history status from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # User2 tries to get fields history status
        response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}/fields_history_status",
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]


class TestRokBudzetowyAccess:
    """Tests for rok_budzetowy access control through parent planowanie."""

    def test_create_rok_for_planowanie_in_different_komorka(self, client, db_session, test_users):
        """Test that user cannot create rok_budzetowy for planowanie in different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # User2 tries to create rok_budzetowy for it
        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_create_rok_for_planowanie_in_same_komorka(self, client, db_session, test_users):
        """Test that user can create rok_budzetowy for planowanie in same komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[1]  # Also komorka 0
        
        # User1 creates planowanie
        payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        create_response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id = create_response.json()["id"]
        
        # User2 (same komorka) creates rok_budzetowy
        rok_payload = {
            "planowanie_budzetu_id": planowanie_id,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        response = client.post(
            "/api/rok_budzetowy",
            json=rok_payload,
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 200
        assert "id" in response.json()

    def test_update_rok_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot update rok_budzetowy from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie and rok
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user1.id)}
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
            headers={"Authorization": str(user1.id)}
        )
        rok_id = rok_response.json()["id"]
        
        # User2 tries to update rok
        update_payload = {
            "field": "limit",
            "value": 60000.00
        }
        response = client.patch(
            f"/api/rok_budzetowy/{rok_id}",
            json=update_payload,
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_rok_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot get rok_budzetowy from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie and rok
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user1.id)}
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
            headers={"Authorization": str(user1.id)}
        )
        rok_id = rok_response.json()["id"]
        
        # User2 tries to get rok
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}",
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_all_rok_filters_by_komorka(self, client, db_session, test_users):
        """Test that get_all rok_budzetowy filters by komorka through parent planowanie."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie and rok in komorka 0
        planowanie_payload1 = {
            "nazwa_projektu": "Project Komorka 0",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        planowanie_response1 = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload1,
            headers={"Authorization": str(user1.id)}
        )
        planowanie_id1 = planowanie_response1.json()["id"]
        
        rok_payload1 = {
            "planowanie_budzetu_id": planowanie_id1,
            "limit": 50000.00,
            "potrzeba": 75000.00
        }
        client.post(
            "/api/rok_budzetowy",
            json=rok_payload1,
            headers={"Authorization": str(user1.id)}
        )
        
        # User2 creates planowanie and rok in komorka 1
        planowanie_payload2 = {
            "nazwa_projektu": "Project Komorka 1",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 1
        }
        planowanie_response2 = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload2,
            headers={"Authorization": str(user2.id)}
        )
        planowanie_id2 = planowanie_response2.json()["id"]
        
        rok_payload2 = {
            "planowanie_budzetu_id": planowanie_id2,
            "limit": 60000.00,
            "potrzeba": 85000.00
        }
        client.post(
            "/api/rok_budzetowy",
            json=rok_payload2,
            headers={"Authorization": str(user2.id)}
        )
        
        # User1 should only see rok from komorka 0
        response1 = client.get(
            "/api/rok_budzetowy",
            headers={"Authorization": str(user1.id)}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 1
        assert data1[0]["planowanie_budzetu_id"] == planowanie_id1
        
        # User2 should only see rok from komorka 1
        response2 = client.get(
            "/api/rok_budzetowy",
            headers={"Authorization": str(user2.id)}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 1
        assert data2[0]["planowanie_budzetu_id"] == planowanie_id2

    def test_get_rok_field_history_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot get rok field history from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie and rok
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user1.id)}
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
            headers={"Authorization": str(user1.id)}
        )
        rok_id = rok_response.json()["id"]
        
        # User2 tries to get field history
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/field_history/limit",
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_rok_fields_history_status_from_different_komorka(self, client, db_session, test_users):
        """Test that user cannot get rok fields history status from different komorka."""
        user1 = test_users[0]  # Komorka 0
        user2 = test_users[2]  # Komorka 1
        
        # User1 creates planowanie and rok
        planowanie_payload = {
            "nazwa_projektu": "Project",
            "budzet": "2024",
            "czesc_budzetowa_kod": "75",
            "dzial_kod": "750",
            "rozdzial_kod": "75011",
            "paragraf_kod": "4210",
            "zrodlo_finansowania_kod": "1",
            "grupa_wydatkow_id": 1,
            "komorka_organizacyjna_id": 0
        }
        planowanie_response = client.post(
            "/api/planowanie_budzetu",
            json=planowanie_payload,
            headers={"Authorization": str(user1.id)}
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
            headers={"Authorization": str(user1.id)}
        )
        rok_id = rok_response.json()["id"]
        
        # User2 tries to get fields history status
        response = client.get(
            f"/api/rok_budzetowy/{rok_id}/fields_history_status",
            headers={"Authorization": str(user2.id)}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]


class TestUserIdTracking:
    """Tests for user_id versioned field tracking."""

    def test_user_id_is_stored_on_create(self, client, db_session, test_users):
        """Test that user_id is stored as versioned field on creation."""
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
        
        response = client.post(
            "/api/planowanie_budzetu",
            json=payload,
            headers={"Authorization": str(user.id)}
        )
        
        assert response.status_code == 200
        planowanie_id = response.json()["id"]
        
        # Verify user_id is stored
        user_id_version = db_session.query(VersionedForeignKeyField).filter_by(
            entity_type="planowanie_budzetu",
            entity_id=planowanie_id,
            field_name="user_id"
        ).first()
        
        assert user_id_version is not None
        assert user_id_version.value_int == user.id

    def test_user_id_not_in_response(self, client, db_session, test_users):
        """Test that user_id is not returned in API responses."""
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
        
        # Get single planowanie
        get_response = client.get(
            f"/api/planowanie_budzetu/{planowanie_id}",
            headers={"Authorization": str(user.id)}
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert "user_id" not in data
        
        # Get all planowania
        get_all_response = client.get(
            "/api/planowanie_budzetu",
            headers={"Authorization": str(user.id)}
        )
        
        assert get_all_response.status_code == 200
        all_data = get_all_response.json()
        assert all(("user_id" not in item) for item in all_data)
