import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional



class RequestRecorder:
    def __init__(self, cassette_dir: str = "cassettes"):
        self.cassette_dir = Path(cassette_dir)
        self.cassette_dir.mkdir(exist_ok=True)
        self.recorded_requests: List[Dict[str, Any]] = []
        self.cassette_file = None
        self.mode = "record"

    def _get_request_hash(
        self, url: str, method: str, body: Optional[str] = None
    ) -> str:
        content = f"{method}:{url}"
        if body:
            content += f":{body}"
        return hashlib.md5(content.encode()).hexdigest()

    def set_cassette(self, name: str, mode: str = "record"):
        self.cassette_file = self.cassette_dir / f"{name}.json"
        self.mode = mode

        if mode == "replay" and self.cassette_file.exists():
            with open(self.cassette_file, "r", encoding="utf-8") as f:
                self.recorded_requests = json.load(f)
        else:
            self.recorded_requests = []

    def save_cassette(self):
        if self.cassette_file and self.mode == "record":
            print(
                f"Saving {len(self.recorded_requests)} requests to {self.cassette_file}"
            )
            with open(self.cassette_file, "w", encoding="utf-8") as f:
                json.dump(self.recorded_requests, f, indent=2)

    def setup_recording(self, page):
        async def handle_request(request):
            if self.mode == "replay":
                request_hash = self._get_request_hash(
                    request.url, request.method, request.post_data
                )
                for recorded in self.recorded_requests:
                    if recorded.get("request_hash") == request_hash:
                        await request.fulfill(
                            status=recorded["response"]["status"],
                            headers=recorded["response"]["headers"],
                            body=recorded["response"]["body"],
                        )
                        return

        async def handle_response(response):
            if self.mode == "record":
                skip_domains = [
                    "adfarm1.adition.com",
                    "doubleclick.net",
                    "google-analytics.com",
                ]
                request = response.request
                if any(domain in request.url for domain in skip_domains):
                    return

                body_content = ""
                if 200 <= response.status < 300:
                    try:
                        body = await response.body()
                        body_content = body.decode("utf-8")
                    except Exception:
                        body_content = ""

                self.recorded_requests.append(
                    {
                        "request_hash": self._get_request_hash(
                            request.url, request.method, request.post_data
                        ),
                        "request": {
                            "url": request.url,
                            "method": request.method,
                            "post_data": request.post_data,
                        },
                        "response": {
                            "status": response.status,
                            "headers": dict(response.headers),
                            "body": body_content,
                        },
                    }
                )

        if self.mode == "replay":
            page.on("request", handle_request)
        elif self.mode == "record":
            page.on("response", handle_response)
