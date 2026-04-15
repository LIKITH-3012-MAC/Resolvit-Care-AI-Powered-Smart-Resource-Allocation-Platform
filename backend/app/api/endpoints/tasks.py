from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.models.task import Task, TaskAssignment
from backend.app.schemas.task import TaskSchema, TaskCreate, TaskUpdate

router = APIRouter()

@router.post("/", response_model=TaskSchema)
async def create_task(
    *,
    db: AsyncSession = Depends(get_db),
    task_in: TaskCreate
) -> Any:
    """
    Create a new task linked to a community report.
    """
    task = Task(
        report_id=task_in.report_id,
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        deadline=task_in.deadline,
        status="open",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get("/", response_model=List[TaskSchema])
async def read_tasks(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve tasks with pagination.
    """
    query = select(Task).offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.get("/{id}", response_model=TaskSchema)
async def read_task_by_id(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get task details including assignments.
    """
    query = select(Task).where(Task.id == id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task
