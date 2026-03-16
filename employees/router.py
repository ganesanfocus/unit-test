from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from db import get_db
from .schemas import EmployeeUpdate, EmployeeCreate

router = APIRouter()
templates = Jinja2Templates(directory="templates/employees")

@router.get("/index", response_class=HTMLResponse)
async def index_page(request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        return RedirectResponse(url="/users/login", status_code=303)
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY emp_id DESC")
    employees = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse(request, "index.html", {"request": request, "employees": employees})

@router.get("/add", response_class=HTMLResponse)
async def add_employee_page(request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        return RedirectResponse(url="/users/login", status_code=303)
    return templates.TemplateResponse(request, "add_employee.html", {"request": request})

@router.post("/add")
async def add_employee(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    department: str = Form(...),
    designation: str = Form(...),
    city: str = Form(...)
):
    user_session = request.cookies.get("user_session")
    if not user_session:
        return RedirectResponse(url="/users/login", status_code=303)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id FROM employees WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return RedirectResponse(url="/employees/add?error=Email+already+exists", status_code=303)
    
    cursor.execute(
        "INSERT INTO employees (fullname, email, mobile, department, designation, city) VALUES (?, ?, ?, ?, ?, ?)",
        (fullname, email, mobile, department, designation, city)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/employees/index?msg=Employee+added+successfully", status_code=303)

@router.get("/api/{emp_id}")
async def get_employee(emp_id: int, request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, fullname, email, mobile, department, designation, city FROM employees WHERE emp_id = ?", (emp_id,))
    employee = cursor.fetchone()
    conn.close()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return dict(employee)

@router.post("/api/edit/{emp_id}")
async def edit_employee(emp_id: int, emp_data: EmployeeUpdate, request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT emp_id FROM employees WHERE emp_id = ?", (emp_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Employee not found")
        
    cursor.execute("""
        UPDATE employees 
        SET fullname = ?, email = ?, mobile = ?, department = ?, designation = ?, city = ?, updated_at = CURRENT_TIMESTAMP
        WHERE emp_id = ?
    """, (emp_data.fullname, emp_data.email, emp_data.mobile, emp_data.department, emp_data.designation, emp_data.city, emp_id))
    conn.commit()
    conn.close()
    return {"message": "Employee updated successfully"}

@router.delete("/api/delete/{emp_id}")
async def delete_employee(emp_id: int, request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
    conn.commit()
    conn.close()
    return {"message": "Employee deleted successfully"}
