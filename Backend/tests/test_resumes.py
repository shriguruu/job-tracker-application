import io


def test_upload_resume_success(client, user_a_auth):
    fake_pdf = io.BytesIO(b"%PDF-1.4 sample pdf file content")
    res = client.post(
        "/api/v1/resumes",
        data={"resume_name": "Software Engineer Resume v1"},
        files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
        headers=user_a_auth["headers"],
    )
    assert res.status_code == 201
    data = res.json()
    assert "resume_id" in data
    assert data["resume_name"] == "Software Engineer Resume v1"


def test_upload_resume_invalid_file_type(client, user_a_auth):
    fake_txt = io.BytesIO(b"this is plain text not pdf")
    res = client.post(
        "/api/v1/resumes",
        data={"resume_name": "Invalid Resume"},
        files={"file": ("resume.txt", fake_txt, "text/plain")},
        headers=user_a_auth["headers"],
    )
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "INVALID_FILE_TYPE"


def test_upload_resume_empty_file(client, user_a_auth):
    empty_pdf = io.BytesIO(b"")
    res = client.post(
        "/api/v1/resumes",
        data={"resume_name": "Empty Resume"},
        files={"file": ("empty.pdf", empty_pdf, "application/pdf")},
        headers=user_a_auth["headers"],
    )
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "EMPTY_FILE"


def test_resume_presigned_download_url(client, user_a_auth):
    fake_pdf = io.BytesIO(b"%PDF-1.4 sample content")
    upload_res = client.post(
        "/api/v1/resumes",
        data={"resume_name": "Downloadable Resume"},
        files={"file": ("my_resume.pdf", fake_pdf, "application/pdf")},
        headers=user_a_auth["headers"],
    )
    resume_id = upload_res.json()["resume_id"]

    url_res = client.get(f"/api/v1/resumes/{resume_id}/download-url", headers=user_a_auth["headers"])
    assert url_res.status_code == 200
    data = url_res.json()
    assert "url" in data
    assert "expires_in" in data
    assert data["expires_in"] > 0


def test_delete_resume_and_set_null_on_application(client, user_a_auth):
    # Upload resume
    fake_pdf = io.BytesIO(b"%PDF-1.4 sample content")
    upload_res = client.post(
        "/api/v1/resumes",
        data={"resume_name": "Delete Test Resume"},
        files={"file": ("del.pdf", fake_pdf, "application/pdf")},
        headers=user_a_auth["headers"],
    )
    resume_id = upload_res.json()["resume_id"]

    # Create application referencing this resume
    app_res = client.post(
        "/api/v1/applications",
        json={"company_name": "Meta", "role_name": "Frontend Eng", "resume_id": resume_id},
        headers=user_a_auth["headers"],
    )
    app_id = app_res.json()["application_id"]
    assert app_res.json()["resume_id"] == resume_id

    # Delete resume
    del_res = client.delete(f"/api/v1/resumes/{resume_id}", headers=user_a_auth["headers"])
    assert del_res.status_code == 204

    # Verify resume is gone
    get_res = client.get(f"/api/v1/resumes/{resume_id}/download-url", headers=user_a_auth["headers"])
    assert get_res.status_code == 404

    # Verify application still exists and resume_id is SET NULL
    app_check = client.get(f"/api/v1/applications/{app_id}", headers=user_a_auth["headers"]).json()
    assert app_check["application_id"] == app_id
    assert app_check["resume_id"] is None
