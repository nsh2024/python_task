from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["taskdb"]
collection = db["taskList"]

# Create FastAPI app
app = FastAPI()

# allow_origins=["https://myflutterapp.web.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to specific domains later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define data model
class Task(BaseModel):
    task: str
    date: str
    status: str

# Convert MongoDB object to dict
def serialize_task(task):
    return {
        "id": str(task["_id"]),
        "task": task["task"],
        "date": task["date"],
        "status": task["status"]
    }
# Add new task
# Create a task
@app.post("/tasks")
def create_task(task: Task):
    result = collection.insert_one(task.dict())
    return {
        "message": "Task created",
        "id": str(result.inserted_id)
    }

# Get all tasks
@app.get("/tasks")
def get_tasks():
    tasks = collection.find()
    return [serialize_task(t) for t in tasks]

# Update a task
@app.put("/tasks/{task_id}")
def update_task(task_id: str, updated_task: Task):
    result = collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": updated_task.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated"}

# Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    result = collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
