from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="SSRF Labs - BreachPoint", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

TIMEOUT = 5.0


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# Level 1  -  Easy  (No protection)
# ---------------------------------------------------------------------------

LEVEL1_CTX = {
    "level": 1,
    "difficulty": "Easy",
    "subtitle": "No Protection",
    "description": (
        "The URL Previewer fetches any URL you provide and displays "
        "the response. There is no validation or filtering of any kind."
    ),
    "hint": (
        "Is there another service running on this server itself? "
        "Try scanning common ports on the loopback address."
    ),
}


@app.get("/level/1", response_class=HTMLResponse)
async def level1_page(request: Request):
    return templates.TemplateResponse(
        "level.html",
        {"request": request, **LEVEL1_CTX, "result": None, "error": None, "url": ""},
    )


@app.post("/level/1", response_class=HTMLResponse)
async def level1_submit(request: Request, url: str = Form(...)):
    result = None
    error = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
            result = resp.text
    except Exception as exc:
        error = f"Request failed: {exc}"

    return templates.TemplateResponse(
        "level.html",
        {"request": request, **LEVEL1_CTX, "result": result, "error": error, "url": url},
    )


# ---------------------------------------------------------------------------
# Level 2  -  Medium  (Blacklist bypass)
# ---------------------------------------------------------------------------

BLACKLIST = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
    "::1",
    "[::1]",
]


def is_blacklisted(url: str) -> bool:
    """Check the raw URL string against a naive keyword blacklist."""
    lower = url.lower()
    for keyword in BLACKLIST:
        if keyword in lower:
            return True
    return False


LEVEL2_CTX = {
    "level": 2,
    "difficulty": "Medium",
    "subtitle": "Blacklist Bypass",
    "description": (
        "The backend blocks common loopback addresses and hostnames such as "
        "127.0.0.1, localhost, and 0.0.0.0. "
        "Can you find an alternative representation that slips through?"
    ),
    "hint": (
        "IP addresses can be expressed in many formats: decimal, "
        "hexadecimal, octal ... Think outside the dotted-quad box."
    ),
}


@app.get("/level/2", response_class=HTMLResponse)
async def level2_page(request: Request):
    return templates.TemplateResponse(
        "level.html",
        {"request": request, **LEVEL2_CTX, "result": None, "error": None, "url": ""},
    )


@app.post("/level/2", response_class=HTMLResponse)
async def level2_submit(request: Request, url: str = Form(...)):
    result = None
    error = None

    if is_blacklisted(url):
        error = "Blocked: the URL contains a blacklisted keyword."
    else:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
                result = resp.text
        except Exception as exc:
            error = f"Request failed: {exc}"

    return templates.TemplateResponse(
        "level.html",
        {"request": request, **LEVEL2_CTX, "result": result, "error": error, "url": url},
    )


# ---------------------------------------------------------------------------
# Level 3  -  Hard  (Whitelist / URL-parser quirks)
# ---------------------------------------------------------------------------

ALLOWED_PREFIX = "http://trusted.breachpoint.io"


def passes_whitelist(url: str) -> bool:
    """Only allow URLs that start with the trusted prefix."""
    return url.startswith(ALLOWED_PREFIX)


LEVEL3_CTX = {
    "level": 3,
    "difficulty": "Hard",
    "subtitle": "Whitelist / Parser Quirks",
    "description": (
        "The backend enforces a strict whitelist: only URLs starting with "
        "http://trusted.breachpoint.io are allowed. "
        "Can you trick the URL parser into reaching the localhost service?"
    ),
    "hint": (
        "The URL spec allows a userinfo component before the host. "
        "What happens when you put the trusted domain in the userinfo "
        "and 127.0.0.1 as the actual host?"
    ),
}


@app.get("/level/3", response_class=HTMLResponse)
async def level3_page(request: Request):
    return templates.TemplateResponse(
        "level.html",
        {"request": request, **LEVEL3_CTX, "result": None, "error": None, "url": ""},
    )


@app.post("/level/3", response_class=HTMLResponse)
async def level3_submit(request: Request, url: str = Form(...)):
    result = None
    error = None

    if not passes_whitelist(url):
        error = "Blocked: URL must start with http://trusted.breachpoint.io"
    else:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
                result = resp.text
        except Exception as exc:
            error = f"Request failed: {exc}"

    return templates.TemplateResponse(
        "level.html",
        {"request": request, **LEVEL3_CTX, "result": result, "error": error, "url": url},
    )
