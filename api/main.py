from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World!"}

