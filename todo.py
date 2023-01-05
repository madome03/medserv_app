import os
import time
import boto3
from typing import Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends 
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
async def root():
    return {"message": "Hello from ToDo API!"}

#get method to take in maitenance requests from html form
@app.get("/create-maitenance-request", response_class=HTMLResponse)
def create_maitenance_request(request: Request):
    return templates.TemplateResponse("create-maitenance-request.html", {"request": request})


#post method which updates db table with the form info based on the selected store location
@app.post("/create-maitenance-request", response_class=HTMLResponse)
def create_maitenance_request(request: Request, form_data: requestform = Depends(requestform.as_form)):
    
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
    table = _get_table()
    table.put_item(Item=Item)
    return templates.TemplateResponse("dashboard.html", {"maitenance-request": Item}, {"request", request})
