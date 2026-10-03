from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Role
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut
from ..security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()

    # Check whether email already exists
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # Create parent account by default
    user = User(
        full_name=data.full_name,
        email=email,
        phone=None,
        password_hash=hash_password(data.password),
        role=Role.parent,
        specialization=None,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenOut(
        access_token=create_access_token(user),
        user=UserOut.model_validate(user)
    )


def _authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(
        select(User).where(User.email == email.lower())
    )

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    return user


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = _authenticate(
        db,
        data.email,
        data.password
    )

    return TokenOut(
        access_token=create_access_token(user),
        user=UserOut.model_validate(user)
    )


@router.post("/token", include_in_schema=False)
def token(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 form login for Swagger Authorize.
    Username = email.
    """

    user = _authenticate(
        db,
        form.username,
        form.password
    )

    return {
        "access_token": create_access_token(user),
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user