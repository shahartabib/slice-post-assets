# -*- coding: utf-8 -*-
"""Marky REST helper — create/list posts via the WORKING nested endpoint.

The `marky` MCP's post endpoints (marky_create_post / marky_list_posts) are broken:
they call the flat /api/posts and get 404. Marky nests posts under the business:
    POST/GET  /api/businesses/{business_id}/posts
and business_id must be in the PATH only (putting it in the body -> 422).

create_draft() makes an unscheduled NEW draft. create_scheduled() (approved by Shahar
2026-07-01 as the new standard) schedules the post to a given Israel-local slot so each
week's posts land on the right Sun 19:30 / Tue 15:00 / Thu 15:00 automatically.
Schedule field is "scheduled_publish_time" (ISO-8601 UTC) with status "SCHEDULED"
(NOT "adhoc_publish_time" — that is the broken MCP's field name and is rejected here).
"""
import json, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

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
    """Create an UNSCHEDULED draft (status NEW). Returns the API response (incl. new post id).
    media_url may be a single URL (str) or a list of URLs (carousel; order preserved)."""
    # API field is restrict_publish_to (NOT publish_to — that 422s "Extra inputs are not permitted", changed ~2026-07-03).
    body = {"caption": caption, "restrict_publish_to": [platform], "status": "NEW"}  # NEW = draft; never schedule/publish
    if media_url:
        body["media_urls"] = media_url if isinstance(media_url, list) else [media_url]
    return _req(f"/api/businesses/{business_id}/posts", "POST", body)   # id in PATH only, NOT in body

def il_to_utc_iso(year, month, day, hour, minute):
    """Israel local wall-clock -> ISO-8601 UTC (handles IDT/IST DST via zoneinfo)."""
    dt = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("Asia/Jerusalem"))
    return dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

def create_scheduled(caption, platform, when_il, media_url=None, business_id=BUSINESS_ID):
    """Create a post SCHEDULED to an Israel-local slot.
    when_il = (year, month, day, hour, minute) in Asia/Jerusalem, e.g. (2026,7,5,19,30).
    Standard slots: FB Sun 19:30, LinkedIn Tue & Thu 15:00 (Israel time)."""
    body = {"caption": caption, "restrict_publish_to": [platform], "status": "SCHEDULED",
            "scheduled_publish_time": il_to_utc_iso(*when_il)}   # field is scheduled_publish_time, NOT adhoc_publish_time
    if media_url:
        body["media_urls"] = media_url if isinstance(media_url, list) else [media_url]
    return _req(f"/api/businesses/{business_id}/posts", "POST", body)   # id in PATH only, NOT in body

def list_posts(status=None, business_id=BUSINESS_ID):
    q = f"?status={status}" if status else "?limit=20"
    return _req(f"/api/businesses/{business_id}/posts{q}")

if __name__ == "__main__":
    d = list_posts("NEW")
    rows = d.get("data", d if isinstance(d, list) else [])
    print(f"{len(rows)} NEW draft(s):")
    for p in rows[:20]:
        print(" -", p.get("id"), p.get("publish_to"), (p.get("caption") or "")[:40].replace("\n", " "))
