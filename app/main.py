from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Session, select

from .database import create_db_and_tables, get_db

app = FastAPI(title="To Do list ig")

# Trigger table creation on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# 1. SQLModel Schemas
