import os
import time
from typing import Optional
from uuid import uuid4
import boto3
from boto3.dynamodb.conditions import Key
from fastapi import (Depends, FastAPI, File, Form, HTTPException, Request, UploadFile)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from mangum import Mangum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re
import logging

app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)

templates = Jinja2Templates(directory="templates")

logger = logging.getLogger('maintenance_request')
logger.setLevel(logging.INFO)


@app.get("/")
async def root():
    return {"message": "Hello from ToDo API!"}

s3_maitenance_request = boto3.resource('s3')

def _get_table():
    table_name = os.environ.get("TABLE_NAME")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    return table


#save maintenance requests
@app.post("/save-maintenance-request")
async def create_maitenance_request(request: Request):

    table = _get_table()

    try:

        data = await request.form()  # get the form data from the request

    except Exception as e:

        logger.error(f'Error getting form data: {e}')
        
        return {'status code': 400, 'body': "Error: missing form data"}

    created_time = int(time.time())

    store_location = data.get('store_location', None)

    if not store_location:

        logger.error('Error: missing store_location')
        
        return {'status code': 400, 'body': "Error: missing store_location in form data"}

    name = data.get('name', None)
    lastname = data.get('lastname', None)
    email = data.get('email', None)
    phonenumber = data.get('phonenumber', None)
    message = data.get('message', None)

    if not all(val is not None for val in (name, lastname, email, phonenumber, message)):

        logger.error('Error: missing fields in form data')
        return {'status code': 400, 'body': "Error: missing fields in form data"}

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        logger.error('Error: invalid email')
        return {'status code': 400, 'body': "Error: invalid email"}

    if not phonenumber.isdigit():
        logger.error('Error: invalid phone number')
        return {'status code': 400, 'body': "Error: invalid phone number"}

    item = {

        'store_location': {'S': store_location},
        'name': {'S': name},
        'lastname': {'S': lastname},
        'email': {'S': email},
        'phonenumber': {'S': phonenumber},
        'message': {'S': message},
        'is_done': {'BOOL': False},
        'created_time': {'N': str(created_time)},
        'request_id': {'S': str(uuid4())}
    }
    try:
    # insert the item into the Dynamodb database
        if 'file' in data:
            file = data['file']

            s3_maitenance_request.Bucket('www.mymedserv.com').upload_file(file.filename, file.file)
    
            item['attachment'] = {'S': file.filename}
    

    except Exception as e:

        logger.error(f'Error uploading attachment to S3: {e}')
        return {'status code': 500, 'body': "Error uploading attachment to S3"}
    
    if 'attachment' in item:
        logger.info("Attachment added successfully")

    else:
        logger.info("Attachment not added")

    try:
        table.update_item(
            Key={
                'store_location': {'S': store_location},
                'created_time': {'N': str(created_time)}
            },
             UpdateExpression='SET #name = :name, #lastname = :lastname, #email = :email, #phonenumber = :phonenumber, #message = :message, #is_done = :is_done, #created_time = :created_time, #request_id = :request_id, #attachment = :attachment',
            ExpressionAttributeNames={
                '#name': 'name',
                '#lastname': 'lastname',
                '#email': 'email',
                '#phonenumber': 'phonenumber',
                '#message': 'message',
                '#is_done': 'is_done',
                '#request_id': 'request_id',
                '#attachment': 'attachment',
            },
             ExpressionAttributeValues={
                ':name': item['name'],
                ':lastname': item['lastname'],
                ':email': item['email'],
                ':phonenumber': item['phonenumber'],
                ':message': item['message'],
                ':is_done': item['is_done'],
                ':request_id': item['request_id'],
                ':attachment': item.get('attachment', {})
            }
        )
    except Exception as e:

        logger.error(f'Error updating item in DynamoDB: {e}')
        return {'status code': 500, 'body': 'Error updating item in DynamoDB'}

    logger.info('Maintenance request added successfully to the database')
    return {'status code': 200, 'body': 'Maintenance request added successfully to the database'}

    


@app.get("/store-names/{store_location}")
async def get_tasks(store_location: str):
    table = _get_table()
    response = table.query(
        KeyConditionExpression=Key("store_location").eq(store_location) 
    )
    if response == None:
        return 0
    else:
        return response["Items"]
    



