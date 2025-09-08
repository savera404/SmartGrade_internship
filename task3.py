from pydantic import BaseModel,Field
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from typing import Optional, Annotated
import json

class Student(BaseModel):

    id: Annotated[int, Field(...,title="Student Id" ,description="Unique id of each student", examples=[1,2])]
    name:Annotated[str,Field(..., max_length=50, min_length= 2,title="Student Name", description="Student's Name")]
    age: Annotated[int, Field(gt=5,lt=100, title="Student's age")]
    roll_no: Annotated[str,Field(title="Student roll no", description="Unique roll no of student")]
    grade: Optional[str]

app=FastAPI()

def load_data():
    with open("students_task3.json","r") as f:
        data=json.load(f)
        return data
    
# to save python dict data into json file 
def save_data(data):
    with open("students_task3.json","w") as f:
        json.dump(data,f)


# - GET /students/ → Get all students. Return the list of all students stored in the JSON file.

@app.get("/students")
def get_students_data():
    data=load_data()
    return data

#Add a new student. Input validation must be handled using Pydantic. If id or roll_number already exists, return an error.

@app.post('/create_student')
def create_student(student: Student):
    data=load_data()

    #check if the student exists in file
    if str(student.id) in data:
        raise HTTPException(status_code=400, detail="Student already exits")
    
    # check if roll_no already exists
    for sid,info in data.items():
        if info['roll_no'] == student.roll_no:
            raise HTTPException(status_code=400, detail="Roll number already exists")
    
    #if not, create student entry, use model dumpt to convert pydantic object to python dict
    data[str(student.id)]=student.model_dump(exclude='id')

    save_data(data)

    return JSONResponse(status_code=201, content={"message":"Student created successfully"})


# - GET /students/{id} → Get a single student by ID. If the student does not exist, return a 404 error.

@app.get("/student/{student_id}")
def get_student_data(student_id:str=Path(...,description="The id of the student", example=4)):
    data=load_data()

    if student_id in data:
        return data[student_id]
    raise HTTPException(status_code=404,detail="Student not found")