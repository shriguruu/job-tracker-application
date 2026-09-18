import io


def test_create_application_success(client, user_a_auth):
    payload = {
        "company_name": "Google",
        "role_name": "Software Engineer",
        "ctc_amount": 3500000.00,
        "ctc_currency": "INR",
        "status": "applied",
        "job_description_url": "https://careers.google.com/jobs/results/123",
        "notes": "Referred by senior engineer",
    }
    res = client.post("/api/v1/applications", json=payload, headers=user_a_auth["headers"])
    assert res.status_code == 201
    data = res.json()
    assert data["company_name"] == "Google"
    assert data["role_name"] == "Software Engineer"
    assert data["status"] == "applied"
    assert data["ctc_currency"] == "INR"
    assert "application_id" in data


def test_applications_user_isolation(client, user_a_auth, user_b_auth):
    # User A creates application
    res_a = client.post(
        "/api/v1/applications",
        json={"company_name": "Company A", "role_name": "Role A"},
        headers=user_a_auth["headers"],
    )
    assert res_a.status_code == 201
    app_a_id = res_a.json()["application_id"]

    # User B creates application
    res_b = client.post(
        "/api/v1/applications",
        json={"company_name": "Company B", "role_name": "Role B"},
        headers=user_b_auth["headers"],
    )
    assert res_b.status_code == 201
    app_b_id = res_b.json()["application_id"]

    # User A list should only have Company A
    list_a = client.get("/api/v1/applications", headers=user_a_auth["headers"]).json()
    assert len(list_a) == 1
    assert list_a[0]["application_id"] == app_a_id
    assert list_a[0]["company_name"] == "Company A"

    # User B cannot access User A's application detail (should 404)
    res_unauth = client.get(f"/api/v1/applications/{app_a_id}", headers=user_b_auth["headers"])
    assert res_unauth.status_code == 404
    assert res_unauth.json()["error"]["code"] == "APPLICATION_NOT_FOUND"


def test_update_and_delete_application(client, user_a_auth):
    # Create application
    res = client.post(
        "/api/v1/applications",
        json={"company_name": "Stripe", "role_name": "Backend Dev", "status": "applied"},
        headers=user_a_auth["headers"],
    )
    app_id = res.json()["application_id"]

    # Update status to 'interview' and add CTC
    update_res = client.put(
        f"/api/v1/applications/{app_id}",
        json={"status": "interview", "ctc_amount": 4000000.00, "notes": "Passed OA"},
        headers=user_a_auth["headers"],
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["status"] == "interview"
    assert float(updated_data["ctc_amount"]) == 4000000.00
    assert updated_data["notes"] == "Passed OA"

    # Delete application
    del_res = client.delete(f"/api/v1/applications/{app_id}", headers=user_a_auth["headers"])
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get(f"/api/v1/applications/{app_id}", headers=user_a_auth["headers"])
    assert get_res.status_code == 404


def test_cannot_attach_other_users_resume(client, user_a_auth, user_b_auth):
    # User B uploads a resume
    fake_pdf = io.BytesIO(b"%PDF-1.4 sample content")
    upload_res = client.post(
        "/api/v1/resumes",
        data={"resume_name": "Bob's Resume"},
        files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
        headers=user_b_auth["headers"],
    )
    assert upload_res.status_code == 201
    bob_resume_id = upload_res.json()["resume_id"]

    # User A tries to create application with Bob's resume
    res = client.post(
        "/api/v1/applications",
        json={"company_name": "Amazon", "role_name": "SDE 1", "resume_id": bob_resume_id},
        headers=user_a_auth["headers"],
    )
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "INVALID_RESUME"
