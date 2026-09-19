import uuid
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.tasks import TaskItem
from app.models.user import User
from app.schemas.tasks import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    on_date: date | None = Query(None, description="Filter to a single day"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(TaskItem).filter(TaskItem.user_id == user.id)
    if on_date:
        start = datetime.combine(on_date, datetime.min.time())
        end = start + timedelta(days=1)
        query = query.filter(TaskItem.scheduled_date >= start, TaskItem.scheduled_date < end)
    return query.order_by(TaskItem.scheduled_date).all()


@router.post("", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = TaskItem(user_id=user.id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: uuid.UUID, payload: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(TaskItem).filter(TaskItem.id == task_id, TaskItem.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/toggle", response_model=TaskRead)
def toggle_task(task_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(TaskItem).filter(TaskItem.id == task_id, TaskItem.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task.is_done = not task.is_done
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(TaskItem).filter(TaskItem.id == task_id, TaskItem.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task)
    db.commit()
