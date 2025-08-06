from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Serve robots.txt
@app.get("/robots.txt", response_class=FileResponse)
async def robots():
    return FileResponse(os.path.join(os.path.dirname(__file__), "robots.txt"), media_type="text/plain")

# Serve sitemap.xml
@app.get("/sitemap.xml", response_class=FileResponse)
async def sitemap():
    return FileResponse(os.path.join(os.path.dirname(__file__), "sitemap.xml"), media_type="application/xml")

# Example root endpoint
@app.get("/")
def home():
    return {"message": "Auto Apply API is live"}








































    
















