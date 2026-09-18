def test_signup_success(client):
    res = client.post(
        "/api/v1/auth/signup",
        json={
            "user_name": "Test User",
            "email": "test@example.com",
            "password": "SecurePassword123",
            "phone_number": "1234567890",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert "user_id" in data
    assert "token" in data
    assert isinstance(data["token"], str)


def test_signup_duplicate_email(client):
    payload = {
        "user_name": "Test User",
        "email": "duplicate@example.com",
        "password": "SecurePassword123",
    }
    res1 = client.post("/api/v1/auth/signup", json=payload)
    assert res1.status_code == 201

    # Attempt signup again with same email in different case
    payload["email"] = "DUPLICATE@EXAMPLE.COM"
    res2 = client.post("/api/v1/auth/signup", json=payload)
    assert res2.status_code == 409
    data = res2.json()
    assert "error" in data
    assert data["error"]["code"] == "EMAIL_EXISTS"


def test_login_success(client):
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "user_name": "Login User",
            "email": "login@example.com",
            "password": "MyPassword123",
        },
    )

    # Login
    res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "MyPassword123",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "user_id" in data
    assert "token" in data


def test_login_invalid_credentials(client):
    res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword",
        },
    )
    assert res.status_code == 401
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_get_current_user_profile(client, user_a_auth):
    res = client.get("/api/v1/auth/me", headers=user_a_auth["headers"])
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "alice@example.com"
    assert data["user_name"] == "Alice Developer"
