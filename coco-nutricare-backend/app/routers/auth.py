from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut
from ..security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    user = User(
        full_name=data.full_name, email=email, phone=data.phone,
        password_hash=hash_password(data.password), role=data.role,
        specialization=data.specialization,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(user), user=UserOut.model_validate(user))


def _authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return user


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = _authenticate(db, data.email, data.password)
    if data.role and user.role != data.role:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"This account is not registered as {data.role.value}")
    return TokenOut(access_token=create_access_token(user), user=UserOut.model_validate(user))


@router.post("/token", include_in_schema=False)
def token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 form login so the Swagger 'Authorize' button works (username = email)."""
    user = _authenticate(db, form.username, form.password)
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
