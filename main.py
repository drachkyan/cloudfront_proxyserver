from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/service")
async def proxy_audio(
    request: Request,
    url: str = Query(..., description="Original audio URL")
):
    headers = {}

    # Пробрасываем Range для audio/video
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.get(url, headers=headers)

    if r.status_code not in (200, 206):
        raise HTTPException(status_code=r.status_code)

    response_headers = {}

    for h in (
        "content-type",
        "content-length",
        "accept-ranges",
        "content-range",
    ):
        if h in r.headers:
            response_headers[h] = r.headers[h]

    response_headers["Access-Control-Allow-Origin"] = "*"
    response_headers["Access-Control-Expose-Headers"] = (
        "Content-Range, Accept-Ranges, Content-Length, Content-Type"
    )

    return StreamingResponse(
        io.BytesIO(r.content),
        status_code=r.status_code,
        headers=response_headers,
        media_type=r.headers.get("content-type"),
    )
