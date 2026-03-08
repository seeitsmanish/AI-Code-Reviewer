import httpx

from app.config import GITHUB_TOKEN, GITHUB_API_BASE

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


async def get_pull_request_files(owner: str, repo: str, pull_number: int):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pull_number}/files"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()


async def get_file_content(contents_url: str) -> list[dict]:
    import base64
    async with httpx.AsyncClient() as client:
        response = await client.get(contents_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        content = base64.b64decode(data["content"]).decode('utf-8')
        lines = content.splitlines()
        return [
            {"line_number": i+1, "content": line}
            for i, line in enumerate(lines)
        ]
