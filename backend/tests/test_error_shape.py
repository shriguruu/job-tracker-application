import uuid


def test_400_validation_error_shape(client):
    # Missing required email and password
    res = client.post("/api/v1/auth/signup", json={})
    assert res.status_code == 400
    data = res.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"]["message"], str)


def test_401_unauthorized_error_shape(client):
    # No Authorization header
    res = client.get("/api/v1/applications")
    assert res.status_code == 401
    data = res.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] in ("UNAUTHORIZED", "INVALID_AUTH_HEADER")


def test_404_not_found_error_shape(client, user_a_auth):
    random_id = uuid.uuid4()
    res = client.get(f"/api/v1/applications/{random_id}", headers=user_a_auth["headers"])
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "APPLICATION_NOT_FOUND"
    assert isinstance(data["error"]["message"], str)


def test_409_conflict_error_shape(client):
    # Duplicate email
    client.post(
        "/api/v1/auth/signup",
        json={"user_name": "U1", "email": "unique@example.com", "password": "Pass12345!"},
    )
    res = client.post(
        "/api/v1/auth/signup",
        json={"user_name": "U2", "email": "unique@example.com", "password": "Pass12345!"},
    )
    assert res.status_code == 409
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "EMAIL_EXISTS"
    assert isinstance(data["error"]["message"], str)
