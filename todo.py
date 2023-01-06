import os
import time
import boto3
from typing import Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends, Request
from mangum import Mangum
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from schemas import requestform

app = FastAPI()

handler = Mangum(app)


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")




@app.get("/")
def root():
    return {"message": "Hello from ToDo API!"}

#get method to take in maitenance requests from html form

@app.get("/create-maitenance-request", response_class=HTMLResponse)
def create_maitenance_request(request: Request):
    return templates.TemplateResponse("create-maitenance-request.html", {"request": request})


#post method which updates db table with the form info based on the selected store location
@app.post("/create-maitenance-request", response_class=HTMLResponse)
def create_maitenance_request_post(request: Request, form_data: requestform = Depends(requestform.as_form)):
    
    request_id = str(uuid4())

    store_location = form_data.store_location

    Item={
        "store_location": store_location,
        "request_id": request_id,
        "name": form_data.name,
        "lastname": form_data.lastname,
        "email": form_data.email,
        "phone": form_data.phone,
        "message": form_data.message,
        "file": form_data.file,
        "created_time": int(time.time())
    }
    print(Item)
    table = _get_table()
    table.put_item(Item=Item)
    return templates.TemplateResponse("dashboard.html", {"maitenance-request": Item}, {"request", request})

    


#get method which shows the amount of pending maitenance requests there are 







def _get_table():
    # Get the table from the environment variable.
    table_name = os.environ.get("TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)

if __name__ == '__main__':
    uvicorn.run(app)

    """
@app.put("/create-task")
async def create_task(put_task_request: PutTaskRequest):
    created_time = int(time.time())
    item = {
        "user_id": put_task_request.user_id,
        "content": put_task_request.content,
        "is_done": False,
        "created_time": created_time,
        "task_id": f"task_{uuid4().hex}",
        "ttl": int(created_time + 86400),  # Expire after 24 hours.
    }

    # Put it into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"task": item}


@app.get("/get-task/{task_id}")
async def get_task(task_id: str):
    # Get the task from the table.
    table = _get_table()
    response = table.get_item(Key={"task_id": task_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return item


@app.get("/list-tasks/{user_id}")
async def list_tasks(user_id: str):
    # List the top N tasks from the table, using the user index.
    table = _get_table()
    response = table.query(
        IndexName="user-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        ScanIndexForward=False,
        Limit=10,
    )
    tasks = response.get("Items")
    return {"tasks": tasks}


@app.put("/update-task")
async def update_task(put_task_request: PutTaskRequest):
    # Update the task in the table.
    table = _get_table()
    table.update_item(
        Key={"task_id": put_task_request.task_id},
        UpdateExpression="SET content = :content, is_done = :is_done",
        ExpressionAttributeValues={
            ":content": put_task_request.content,
            ":is_done": put_task_request.is_done,
        },
        ReturnValues="ALL_NEW",
    )
    return {"updated_task_id": put_task_request.task_id}


@app.delete("/delete-task/{task_id}")
async def delete_task(task_id: str):
    # Delete the task from the table.
    table = _get_table()
    table.delete_item(Key={"task_id": task_id})
    return {"deleted_task_id": task_id}

@app.post("/create-user")
async def create_user(user_id: str):
    # Create a new user in the users table
    table = _get_users_table()
    table.put_item(Item={"user_id": user_id})
    return {"user_id": user_id}"""

