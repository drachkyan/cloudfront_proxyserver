from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

CLOUDFRONT_DOMAIN = "https://{bucket}.cloudfront.net"

@app.get("/service/{bucket}/{folder}/{file_id}")
async def proxy_audio(request: Request, bucket: str, folder: str, file_id: str):
    original_url = f"https://{bucket}.cloudfront.net/{folder}/{file_id}"

    headers = {}
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(original_url, headers=headers)

    if r.status_code not in (200, 206):
        raise HTTPException(status_code=r.status_code)

    response_headers = {}
    for h in ("content-type", "content-length", "accept-ranges", "content-range"):
        if h in r.headers:
            response_headers[h] = r.headers[h]

    return Response(
        content=r.content,
        status_code=r.status_code,
        headers=response_headers,
    )
