import json

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200


def test_crud_comment(client):
    # Create
    payload = {"post_id": "post-xyz", "content": "Hola mundo"}
    r = client.post("/v1/comments", data=json.dumps(payload), headers={
        "Content-Type": "application/json",
        "X-User-Id": "user-1"
    })
    assert r.status_code == 201
    cid = r.get_json()["id"]

    # List
    r = client.get("/v1/comments?post_id=post-xyz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total"] >= 1

    # Update
    r = client.patch(f"/v1/comments/{cid}", data=json.dumps({"content": "Editado"}), headers={
        "Content-Type": "application/json",
        "X-User-Id": "user-1"
    })
    assert r.status_code == 200

    # Delete
    r = client.delete(f"/v1/comments/{cid}", headers={"X-User-Id": "user-1"})
    assert r.status_code == 200