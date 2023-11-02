from fastapi import FastAPI, HTTPException
from aiohttp import ClientSession
from aiohttp import ClientConnectorError
import yaml
import json
from urllib.parse import urlparse
from validators import url as url_validator

app = FastAPI()


@app.get("/")
@app.post("/")
async def parse_url(url: str):
    # Validate the URL
    if not url_validator(url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    # Check if the URL ends with .json
    parsed_url = urlparse(url)
    if parsed_url.path.endswith('.json'):
        return {"detail": "URL points to a JSON file"}

    async with ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=404, detail="Unable to fetch URL")
                
                content = await response.text()

                try:
                    parsed = yaml.safe_load(content)
                    return json.dumps(parsed)
                except yaml.YAMLError as e:
                    raise HTTPException(status_code=400, detail="Unable to parse YAML")
        except ClientConnectorError:
            raise HTTPException(status_code=500, detail="A remote HTTP error occurred")
