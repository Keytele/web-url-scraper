import json
import re
import html
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

base_url = input("Paste a Reddit URL ensure you add a .json to the extension: ").strip()
target_sub = input("Target subreddit eg. AITA: ").strip()

if not base_url.startswith(("http://", "https://")):
    base_url = "https://" + base_url
    
finalised_url = base_url if base_url.endswith(".json") else base_url + ".json"

target_sub = target_sub.removeprefix("/r").strip()

req = Request(base_url, headers = {"User-Agent": "Mozilla/5.0 (Python/Requests)"})

try:
    with urlopen(req) as resp:
        raw = resp.read()
        try:
            data_json = json.loads(raw)
        except json.JSONDecodeError:
            preview = raw[:300].decode("utf-8", "replace")
            ctype = resp.headers.get("Content-Type", "<unknown>")
            raise RuntimeError(
                "Response was not JSON.\n"
                f"Content-Type: {ctype}\n"
                f"Preview:\n{preview}"
            )

except HTTPError as e:
    raise SystemExit(f"HTTP error {e.code}: {e.reason} when fetching {base_url}")
except URLError as e:
    raise SystemExit(f"Network error: {e.reason}")
    
URL_RE = re.compile(r'https?://[^\s"<>)\]]+')
TRAILING_JUNK = '.,;:!?)\]»›…' 

def clean_url(u: str) -> str:
    u = u.rstrip(TRAILING_JUNK)
    # If there's an unmatched closing paren at the end, trim it
    while u.endswith(")") and u.count("(") < u.count(")"):
        u = u[:-1]
    return u

def get_urls(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from get_urls(v)
    elif isinstance(o, list):
        for v in o:
            yield from get_urls(v)
    elif isinstance(o, str):
        s = html.unescape(o)
        yield from URL_RE.findall(s)
        
needle = f"/r/{target_sub.lower()}/"

def canonical(u: str) -> str:
    if u.endswith("/"):
        u = u[:-1]
    return u

filtered = sorted({canonical(u) for u in get_urls(data_json) if needle in u.lower()})

with open("links.txt", "a") as f:
    if filtered:
        for url in filtered:
            print(url, file=f)
    else:
        print(f"No links found for /r/{target_sub}/ in that JSON.")
        
        
print("Your links have been saved to links.txt!")