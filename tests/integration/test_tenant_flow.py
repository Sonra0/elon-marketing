"""End-to-end (REST-only) flow:

  POST /tenants -> JWT  -> GET /tenants/me ->
  insert a Post directly via API helpers ->
  POST /posts/{id}/decide approve -> verify state transition.
"""

from __future__ import annotations

from uuid import UUID

import pytest

pytestmark = pytest.mark.integration


def test_tenant_create_and_me(app_client):
    r = app_client.post("/tenants", json={"name": "Test Brand"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "jwt" in body and "telegram_link_token" in body
    auth = {"Authorization": f"Bearer {body['jwt']}"}

    me = app_client.get("/tenants/me", headers=auth)
    assert me.status_code == 200
    j = me.json()
    assert j["tenant_id"] == body["tenant_id"]
    assert j["telegram_linked"] is False


def test_post_decide_flow(app_client, monkeypatch):
    # Don't actually queue a Celery publish.
    monkeypatch.setattr("elon.workers.tasks.publish.publish_post.delay", lambda *_: None)

    r = app_client.post("/tenants", json={"name": "DecideTest"})
    assert r.status_code == 200
    body = r.json()
    auth = {"Authorization": f"Bearer {body['jwt']}"}
    tenant_id = UUID(body["tenant_id"])

    # Insert a draft post directly through the DB session.
    import elon.core.db as core_db
    from elon.core.models import Post
    s = core_db.SessionLocal()
    try:
        p = Post(tenant_id=tenant_id, platform="ig", state="review",
                 idea="x", hook="y", caption="z", cta="cta", media_asset_ids=[],
                 score_json={"impact": 1, "effort": 1, "risk": 1},
                 requires_human_review=True)
        s.add(p); s.commit()
        post_id = str(p.id)
    finally:
        s.close()

    listed = app_client.get("/posts", headers=auth)
    assert listed.status_code == 200
    assert any(x["id"] == post_id for x in listed.json())

    decided = app_client.post(f"/posts/{post_id}/decide",
                              json={"decision": "approve"}, headers=auth)
    assert decided.status_code == 200
    assert decided.json()["state"] == "approved"
