import requests

def safe_json(r):
    try:
        return r.json()
    except Exception:
        return None


def login(api_base, username, password):
    r = requests.post(
        f"{api_base}/auth/login",
        data={"username": username, "password": password},
        timeout=15,
    )
    return r.status_code, safe_json(r), r.text


def create_account(api_base, email, username, password):
    r = requests.post(
        f"{api_base}/users/",
        json={"email": email, "username": username, "password": password},
        timeout=15,
    )
    return r.status_code, safe_json(r), r.text


def list_files(api_base, headers):
    r = requests.get(f"{api_base}/files", headers=headers, timeout=15)
    return r.status_code, safe_json(r), r.text


def upload_file(api_base, headers, uploaded):
    files = {
        "uploaded": (
            uploaded.name,
            uploaded.getvalue(),
            uploaded.type or "application/octet-stream",
        )
    }
    r = requests.post(
        f"{api_base}/files/upload",
        headers=headers,
        files=files,
        timeout=60,
    )
    return r.status_code, safe_json(r), r.text


def download_file(api_base, headers, file_id):
    r = requests.get(
        f"{api_base}/files/{file_id}/download",
        headers=headers,
        timeout=60,
    )
    return r.status_code, r.content, r.text


def delete_file(api_base, headers, file_id):
    r = requests.delete(
        f"{api_base}/files/{file_id}",
        headers=headers,
        timeout=15,
    )
    return r.status_code, r.text