from fastapi import Form, File, UploadFile
from pydantic import BaseModel

class requestform(BaseModel):
    name: str
    lastname: str
    email: str
    phone: str
    message: str
    file: UploadFile

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        lastname: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        message: str = Form(...),
        file: UploadFile = File(...)
    ):
        return cls(
            name=name,
            lastname=lastname,
            email=email,
            phone=phone,
            message=message,
            file=file
        )
