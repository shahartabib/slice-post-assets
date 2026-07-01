# -*- coding: utf-8 -*-
"""Marky REST helper — create/list posts via the WORKING nested endpoint.

The `marky` MCP's post endpoints (marky_create_post / marky_list_posts) are broken:
they call the flat /api/posts and get 404. Marky nests posts under the business:
    POST/GET  /api/businesses/{business_id}/posts
and business_id must be in the PATH only (putting it in the body -> 422).

DRAFT-ONLY: create_draft() always uses status "NEW" (unscheduled). It never schedules
or publishes. Do NOT add adhoc_publish_time here — scheduling stays a manual Shahar step.
"""
import json, urllib.request

KEY_FILE = r"C:/Users/Shahar Tabib/OneDrive - Sliceknowledge.com/Slice/שיווק סלייס/כלי שיווק/Marky API.txt"
BUSINESS_ID = "e1db849d-f9c8-410d-ac24-ddf45f0f8ea6"   # Slice Knowledge Transfer
BASE = "https://api.mymarky.ai"
# platform strings for this account: "facebook" (page הפרסומים שלי) / "linkedInProfile" (Shahar Tabib)

def _key():
    return open(KEY_FILE, encoding="utf-8-sig").read().strip()

def _req(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())

def create_draft(caption, platform, media_url=None, business_id=BUSINESS_ID):
    """Create an UNSCHEDULED draft (status NEW). Returns the API response (incl. new post id)."""
    body = {"caption": caption, "publish_to": [platform], "status": "NEW"}  # NEW = draft; never schedule/publish
    if media_url:
        body["media_urls"] = [media_url]
    return _req(f"/api/businesses/{business_id}/posts", "POST", body)   # id in PATH only, NOT in body

def list_drafts(status="NEW", business_id=BUSINESS_ID):
    return _req(f"/api/businesses/{business_id}/posts?status={status}")

if __name__ == "__main__":
    d = list_drafts()
    rows = d.get("data", d if isinstance(d, list) else [])
    print(f"{len(rows)} NEW draft(s):")
    for p in rows[:20]:
        print(" -", p.get("id"), p.get("publish_to"), (p.get("caption") or "")[:40].replace("\n", " "))
