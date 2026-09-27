from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..access import get_child_for_user
from ..database import get_db
from ..models import Child, GrowthMeasurement, Role, User
from ..schemas import ChildCreate, ChildOut, ChildUpdate
from ..security import get_current_user, require_roles

router = APIRouter(prefix="/children", tags=["Children"])
parent_only = require_roles(Role.parent)


@router.get("", response_model=list[ChildOut])
def list_children(user: User = Depends(parent_only)):
    return user.children


@router.post("", response_model=ChildOut, status_code=201)
def add_child(data: ChildCreate, db: Session = Depends(get_db), user: User = Depends(parent_only)):
    child = Child(parent_id=user.id, **data.model_dump())
    db.add(child)
    db.flush()
    if data.weight_kg:
        db.add(GrowthMeasurement(child_id=child.id, measured_on=date.today(),
                                 weight_kg=data.weight_kg, height_cm=data.height_cm))
    db.commit()
    db.refresh(child)
    return child


@router.get("/{child_id}", response_model=ChildOut)
def get_child(child_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_child_for_user(db, child_id, user)


@router.patch("/{child_id}", response_model=ChildOut)
def update_child(child_id: int, data: ChildUpdate, db: Session = Depends(get_db),
                 user: User = Depends(parent_only)):
    child = get_child_for_user(db, child_id, user, write=True)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(child, k, v)
    db.commit()
    db.refresh(child)
    return child


@router.delete("/{child_id}", status_code=204)
def delete_child(child_id: int, db: Session = Depends(get_db), user: User = Depends(parent_only)):
    db.delete(get_child_for_user(db, child_id, user, write=True))
    db.commit()
