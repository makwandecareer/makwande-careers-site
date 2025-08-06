from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Mount Bootstrap & other static files
app.mount("/static", StaticFiles(directory="bootstrap-5.0.2-dist"), name="static")

# Serve HTML files from project root
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("index.html")

@app.get("/{page_name}", response_class=HTMLResponse)
async def serve_page(page_name: str):
    """
    Dynamically serve any HTML page in the project directory.
    Example: /login.html → serves login.html
    """
    file_path = os.path.join(".", page_name)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return HTMLResponse(content="<h1>404 - Page Not Found</h1>", status_code=404)

# Example backend route for jobs API
@app.get("/api/jobs")
async def get_jobs():
    return {"jobs": []}  # Replace with real job fetching logic

# Example backend route for subscription
@app.post("/api/subscribe")
async def subscribe(email: str = Form(...)):
    return {"message": f"Subscription started for {email}"}

# Health check for Render
@app.head("/")
async def health_check():
    return HTMLResponse(content="OK", status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
 "skills": "Project Management, Agile", "status": "pending"},





































    
















