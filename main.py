from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Serve Bootstrap & static files
app.mount("/static", StaticFiles(directory="bootstrap-5.0.2-dist"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("index.html")


@app.get("/{page_name}", response_class=HTMLResponse)
async def serve_page(page_name: str):
    """Serve HTML files from root folder."""
    file_path = os.path.join(".", page_name)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return HTMLResponse(content="<h1>404 - Page Not Found</h1>", status_code=404)


@app.get("/api/jobs")
async def get_jobs():
    return {"jobs": []}


@app.post("/api/subscribe")
async def subscribe(email: str = Form(...)):
    return {"message": f"Subscription started for {email}"}


@app.get("/get-applicants")
async def get_applicants(recruiter_id: str):
    return [
        {
            "candidate_id": "123",
            "name": "John D.",
            "email": "john@example.com",
            "phone": "060-123-4567",
            "skills": "Python, Data Analysis",
            "status": "approved"
        },
        {
            "candidate_id": "124",
            "name": "Jane S.",
            "email": "jane@example.com",
            "phone": "060-987-6543",
            "skills": "Project Management, Agile",
            "status": "pending"
        },
        {
            "candidate_id": "125",
            "name": "Michael B.",
            "email": "michael@example.com",
            "phone": "060-555-1111",
            "skills": "Business Analysis, SQL",
            "status": "declined"
        }
    ]


@app.head("/")
async def health_check():
    return HTMLResponse(content="OK", status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)







































    
















