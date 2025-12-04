from asyncio import tasks
from optparse import Option
from tkinter import S
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import re
from typing import List, Optional
from fastapi.responses import FileResponse

import json
import os

import databaseConnect


class Student(BaseModel):
    name:str
    mobile:int
    age:int

class New_student(Student):
    id:int

class StudentID(BaseModel):
    sid: Optional[int] = None

students : [New_student ] = []
student_id = 1

# databaseConnect()

DATA_FILE = "students.json"

def save_students_to_file():
    with open(DATA_FILE, "w") as f:
        json.dump([student.dict() for student in students], f)

def load_students_from_file():
    global students, student_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            students.clear()
            for s in data:
                students.append(New_student(**s))
            if students:
                student_id = max(s.id for s in students) + 1
    else:
        students.clear()
        student_id = 1



app = FastAPI()
load_students_from_file()













@app.get("/")
def read_root():
    return {"message": "Hello, Welcome to Python World!"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

# Get List of all Students
@app.get("/student_list/")
def get_student_list():
    return {"message": "Students fetched successfully", "students": students}

# Add new student
@app.post("/student/")
def create_user(user:Student):
    global student_id
    
    # Mobile number validation (custom)
    mobile_str = str(user.mobile)
    if not re.fullmatch(r"^[6-9]\d{9}$", mobile_str):
        return {"message": "Invalid mobile number format", "status_code": 202}

    # Duplicate check
    for student in students:
        if student.mobile == user.mobile:
            return {"message": "Student with mobile number already exists", "status_code": 202}
            # return HTTPException(status_code=400, detail="Task with this ID already exists")

    new_student = New_student(id=student_id, name=user.name,age=user.age,mobile=user.mobile)
    students.append(new_student)
    save_students_to_file()
    student_id += 1
    return {"message": "Student added successfully", "student": user}


# Update student data
@app.put("/update_student/")
def update_student_record(s:Optional[New_student] = None):
    if not s:
        return {"message": "Parameter missing", "status_code": 204}
    tempSt = None
    for student in students:
        if student.mobile == s.mobile:
            return {"message": "Mobile number already exists", "status_code": 202}

    for st in students:
        if st.id == s.id:
            st.name = s.name
            st.age = s.age
            st.mobile = s.mobile
            return {"message": "Student data updated sucessfully", "status_code": 200}
    return {"message": "Student not found", "status_code": 202}

    

# Delete student data
@app.delete("/delete_student/")
def delete_student_record(id:StudentID):
    print("sid",id.sid)
    if id.sid is None :
        return {"message": "Parameter sid missing", "status_code": 204}
    tempSt = None
    for student in students:
        if student.id == id.sid:
            students.remove(student)
            save_students_to_file()
            return {"message": "Student Deleted successfully", "status_code": 200}

    return {"message": "Student not found", "status_code": 202}

# Download student data
@app.get("/download_students/")
def download_students_file():
    return FileResponse("students.json", media_type='application/json', filename="students.json")

