from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ChildProfile, User
from app.schemas import ChildProfileCreate, ChildProfileUpdate, ChildProfileResponse
from app.security import get_current_user  # JWT Authentication helper

router = APIRouter(
    prefix="/v1/children",
    tags=["Child Profiles"]
)

# CN-67: Add Child Profile API
@router.post("", response_model=ChildProfileResponse, status_code=status.HTTP_201_CREATED)
def create_child_profile(
    child: ChildProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    child_data = child.model_dump()

    # Schema-র ফিল্ডগুলোকে DB Model-এর ফিল্ডের সাথে ম্যাপ করা হলো
    db_child = ChildProfile(
        name=child_data.get("name"),
        gender=child_data.get("gender"),
        date_of_birth=child_data.get("date_of_birth"),
        birth_height=child_data.get("height_cm") or child_data.get("birth_height"),
        birth_weight=child_data.get("weight_kg") or child_data.get("birth_weight"),
        food_allergies=[child_data.get("allergies")] if isinstance(child_data.get("allergies"), str) else (child_data.get("food_allergies") or []),
        medicine_allergies=child_data.get("medicine_allergies") or [],
        parent_id=current_user.id
    )

    db.add(db_child)
    db.commit()
    db.refresh(db_child)

    # Response Model এর ফিল্ডগুলোর সাথে DB Model এর কলামগুলো নিখুঁতভাবে ম্যাপ করে রিটার্ন
    allergies_str = ", ".join(db_child.food_allergies) if isinstance(db_child.food_allergies, list) else (db_child.food_allergies or "None")

    return ChildProfileResponse(
        id=db_child.id,
        name=db_child.name,
        gender=db_child.gender,
        date_of_birth=db_child.date_of_birth,
        height_cm=db_child.birth_height,
        weight_kg=db_child.birth_weight,
        blood_group=child_data.get("blood_group"),
        allergies=allergies_str,
        parent_id=db_child.parent_id,
        created_at=db_child.created_at
    )

# Get All Children for Logged-in Parent
@router.get("", response_model=List[ChildProfileResponse])
def get_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    children_list = db.query(ChildProfile).filter(ChildProfile.parent_id == current_user.id).all()
    
    result = []
    for c in children_list:
        allergies_str = ", ".join(c.food_allergies) if isinstance(c.food_allergies, list) else (c.food_allergies or "None")
        result.append(ChildProfileResponse(
            id=c.id,
            name=c.name,
            gender=c.gender,
            date_of_birth=c.date_of_birth,
            height_cm=c.birth_height,
            weight_kg=c.birth_weight,
            blood_group=None,
            allergies=allergies_str,
            parent_id=c.parent_id,
            created_at=c.created_at
        ))
    return result

# CN-68: Update Child Profile API
@router.put("/{child_id}", response_model=ChildProfileResponse)
def update_child_profile(
    child_id: int,
    child_update: ChildProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_child = db.query(ChildProfile).filter(
        ChildProfile.id == child_id, 
        ChildProfile.parent_id == current_user.id
    ).first()

    if not db_child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Child profile not found or unauthorized"
        )

    update_data = child_update.model_dump(exclude_unset=True)
    
    # Update mapping handle করা হলো
    if "height_cm" in update_data:
        db_child.birth_height = update_data.pop("height_cm")
    if "weight_kg" in update_data:
        db_child.birth_weight = update_data.pop("weight_kg")
    if "allergies" in update_data:
        allergies_val = update_data.pop("allergies")
        db_child.food_allergies = [allergies_val] if isinstance(allergies_val, str) else allergies_val

    for key, value in update_data.items():
        if hasattr(db_child, key):
            setattr(db_child, key, value)

    db.commit()
    db.refresh(db_child)

    allergies_str = ", ".join(db_child.food_allergies) if isinstance(db_child.food_allergies, list) else (db_child.food_allergies or "None")

    return ChildProfileResponse(
        id=db_child.id,
        name=db_child.name,
        gender=db_child.gender,
        date_of_birth=db_child.date_of_birth,
        height_cm=db_child.birth_height,
        weight_kg=db_child.birth_weight,
        blood_group=None,
        allergies=allergies_str,
        parent_id=db_child.parent_id,
        created_at=db_child.created_at
    )

# CN-69: Delete Child Profile API
@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child_profile(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_child = db.query(ChildProfile).filter(
        ChildProfile.id == child_id, 
        ChildProfile.parent_id == current_user.id
    ).first()

    if not db_child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Child profile not found or unauthorized"
        )

    db.delete(db_child)
    db.commit()
    return None