from fastapi import FastAPI
from app.github_client import get_file_content, get_pull_request_files
from app.diff_parser import parse_patch

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/review/{owner}/{repo}/{pull_number}")
async def review_pull_request(owner: str, repo: str, pull_number: int):
    files = await get_pull_request_files(owner, repo, pull_number)

    for f in files:
        f["patch"] = parse_patch(f.get("patch", ""))

    return {"files": files}
