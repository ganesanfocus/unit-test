from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from users.router import router as users_router
from employees.router import router as employees_router
from db import init_db

# Initialize database
init_db()

app = FastAPI()

# Include routers
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(employees_router, prefix="/employees", tags=["Employees"])

@app.get("/")
async def root():
    return RedirectResponse(url="/users/login", status_code=303)
