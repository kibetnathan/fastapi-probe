from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Session, select
from typing import List, Optional

from .database import create_db_and_tables, get_db

app = FastAPI(title="To Do list ig")

# Trigger table creation on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# 1. SQLModel Schemas
# Database/API


# Base schema with shared fields
class TodoBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    completed: bool = Field(default=False)


# This represents the db table itself


class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# DTO for creating task


class TodoCreate(TodoBase):
    pass


# DTO for updating task


class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# 2. API Endpoints

# Create TO DO


@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo.model_validate(todo)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


# GET all Todos(optional search filter)


@app.get("/todos/", response_model=List[Todo])
def read_todos(completed: Optional[bool] = None, db: Session = Depends(get_db)):
    query = select(Todo)
    if completed is not None:
        query = query.where(Todo.completed == completed)

    results = db.exec(query).all()
    return results


# GET Todo by ID


@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


# UPDATE Todo


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Extract only data sent by client
    update_data = todo_update.model_dump(exclude_unset=True)

    # Overwrite the existing db record
    for key, value in update_data.items():
        setattr(db_todo, key, value)

    db.add(db_todo)
    db.commit()
    db.refresh()
    return db_todo


# DELETE Todo


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(db_todo)
    db.commit()
    return {"ok": True, "message": f"Successfully deleted Todo task #{todo_id}"}
