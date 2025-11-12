import requests

BASE_URL = "http://127.0.0.1:5000"

def login(email, password):
    url = f"{BASE_URL}/api/login"
    response = requests.post(url, json={"email": email, "password": password})
    return response.json()

def transaction_out(token, part_id, quantity, machine_id, user_id):
    url = f"{BASE_URL}/api/transaction/out"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json={
        "part_id": part_id,
        "quantity": quantity,
        "machine_id": machine_id,
        "user_id": user_id
    }, headers=headers)
    return response.json()

def transaction_in(token, part_id, quantity, user_id):
    url = f"{BASE_URL}/api/transaction/in"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json={
        "part_id": part_id,
        "quantity": quantity,
        "user_id": user_id
    }, headers=headers)
    return response.json()

def extract_part_id(text):
    # Text format = "PART:2"
    try:
        return text.split(":")[1]
    except:
        return text


def get_machines(token):
    url = f"{BASE_URL}/api/machines"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()