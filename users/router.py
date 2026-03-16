from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import hashlib
from typing import Optional

from db import get_db
from .schemas import UserUpdate

router = APIRouter()
templates = Jinja2Templates(directory="templates/users")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"request": request})

@router.post("/register")
async def register_user(
    fullname: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    gender: str = Form(...),
    city: str = Form(...)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return RedirectResponse(url="/users/register?error=Email+already+registered", status_code=303)
    
    hashed_pwd = hash_password(password)
    cursor.execute(
        "INSERT INTO users (fullname, email, mobile, password, gender, city) VALUES (?, ?, ?, ?, ?, ?)",
        (fullname, email, mobile, hashed_pwd, gender, city)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/users/login?msg=Registered+successfully", status_code=303)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@router.post("/login")
async def login_user(
    email: str = Form(...),
    password: str = Form(...)
):
    conn = get_db()
    cursor = conn.cursor()
    hashed_pwd = hash_password(password)
    cursor.execute("SELECT user_id FROM users WHERE email = ? AND password = ?", (email, hashed_pwd))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return RedirectResponse(url="/users/login?error=Invalid+credentials", status_code=303)
        
    response = RedirectResponse(url="/users/index", status_code=303)
    response.set_cookie(key="user_session", value=str(user["user_id"]))
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/users/login", status_code=303)
    response.delete_cookie("user_session")
    return response

@router.get("/index", response_class=HTMLResponse)
async def index_page(request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        return RedirectResponse(url="/users/login", status_code=303)
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY user_id DESC")
    users = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse(request, "index.html", {"request": request, "users": users})

@router.get("/add", response_class=HTMLResponse)
async def add_user_page(request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        return RedirectResponse(url="/users/login", status_code=303)
    return templates.TemplateResponse(request, "add_user.html", {"request": request})

@router.post("/add")
async def add_user(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    gender: str = Form(...),
    city: str = Form(...)
):
    user_session = request.cookies.get("user_session")
    if not user_session:
        return RedirectResponse(url="/users/login", status_code=303)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return RedirectResponse(url="/users/add?error=Email+already+exists", status_code=303)
    
    hashed_pwd = hash_password(password)
    cursor.execute(
        "INSERT INTO users (fullname, email, mobile, password, gender, city) VALUES (?, ?, ?, ?, ?, ?)",
        (fullname, email, mobile, hashed_pwd, gender, city)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/users/index?msg=User+added+successfully", status_code=303)

@router.get("/api/{user_id}")
async def get_user(user_id: int, request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, fullname, email, mobile, gender, city FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

@router.post("/api/edit/{user_id}")
async def edit_user(user_id: int, user_data: UserUpdate, request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    cursor.execute("""
        UPDATE users 
        SET fullname = ?, email = ?, mobile = ?, gender = ?, city = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (user_data.fullname, user_data.email, user_data.mobile, user_data.gender, user_data.city, user_id))
    conn.commit()
    conn.close()
    return {"message": "User updated successfully"}

@router.delete("/api/delete/{user_id}")
async def delete_user(user_id: int, request: Request):
    user_session = request.cookies.get("user_session")
    if not user_session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "User deleted successfully"}
