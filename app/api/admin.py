from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import User, AnalysisLog
from typing import List
from pydantic import BaseModel

router = APIRouter()

class UserSchema(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: int

    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_users: int
    total_requests: int
    error_rate: float
    avg_latency: float

@router.get("/users", response_model=List[UserSchema])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/stats", response_model=SystemStats)
def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    logs = db.query(AnalysisLog).all()
    
    total_requests = len(logs)
    errors = len([l for l in logs if l.status == "error"])
    error_rate = (errors / total_requests * 100) if total_requests > 0 else 0
    
    avg_latency = sum([l.latency_ms for l in logs]) / total_requests if total_requests > 0 else 0
    
    return {
        "total_users": total_users,
        "total_requests": total_requests,
        "error_rate": round(error_rate, 2),
        "avg_latency": round(avg_latency, 2)
    }
