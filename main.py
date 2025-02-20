from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

# Load Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/calculate", response_class=HTMLResponse)
async def calculate_interest(
    request: Request,
    principal: float = Form(...),
    rate: float = Form(...),
    time: float = Form(...)
):
    interest = (principal * rate * time) / 100  # Simple interest formula
    return templates.TemplateResponse(
        "result.html",
        {"request": request, "interest": interest, "principal": principal, "rate": rate, "time": time}
    )

# Run with: uvicorn main:app --reload
