# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
from typing import Optional, Dict, Any

app = FastAPI(title="HTTP Request Proxy")

class RequestModel(BaseModel):
    url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 30

class ResponseModel(BaseModel):
    status_code: int
    headers: Dict[str, str]
    body: Any
    elapsed_seconds: float

@app.post("/proxy", response_model=ResponseModel)
async def proxy_request(request_data: RequestModel):
    try:
        method = request_data.method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            raise HTTPException(status_code=400, detail="Unsupported HTTP method")

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=request_data.url,
                headers=request_data.headers,
                json=request_data.body if method not in ["GET", "HEAD"] else None,
                params=request_data.params,
                timeout=request_data.timeout
            )

            # Convert headers to dict as some may be non-string
            headers_dict = dict(response.headers)
            headers_str = {k: str(v) for k, v in headers_dict.items()}

            return ResponseModel(
                status_code=response.status_code,
                headers=headers_str,
                body=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                elapsed_seconds=response.elapsed.total_seconds()
            )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)