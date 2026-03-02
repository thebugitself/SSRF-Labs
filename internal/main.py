from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Internal Admin Service", docs_url=None, redoc_url=None)

FLAG = "FLAG{ssrf_m4st3r_0f_th3_1nt3rn4l_n3tw0rk}"
SECRET_DATA = {
    "admin_credentials": {
        "username": "admin",
        "password": "S3cur3P@ssw0rd!2026",
    },
    "database": {
        "host": "db.internal.corp",
        "port": 5432,
        "name": "production",
        "user": "db_admin",
        "password": "db_p@ss_!nternal",
    },
    "api_keys": {
        "stripe": "sk_live_FAKE_KEY_4242424242424242",
        "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    },
    "notes": "This data is only accessible from the internal network.",
}


@app.get("/")
async def root():
    return {"service": "Internal Admin Panel", "status": "running"}


@app.get("/flag")
async def get_flag(request: Request):
    return {"flag": FLAG, "message": "You have successfully exploited SSRF to reach the internal service."}


@app.get("/secret-data")
async def get_secret_data(request: Request):
    return JSONResponse(content=SECRET_DATA)


@app.get("/health")
async def health():
    return {"status": "healthy"}
