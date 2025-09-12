from pydantic import BaseModel,Field, EmailStr, computed_field
from datetime import datetime,timezone
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Path, Body, Query
from fastapi.responses import JSONResponse
from typing import Optional, Annotated
import json
from collections import defaultdict

class StudentCreate(BaseModel):

    name:Annotated[str,Field(..., max_length=50, min_length= 2,title="Student Name", description="Student's Name")]
    email:Annotated[EmailStr,Field(...,title="student's email")]
    age: Annotated[int, Field(...,ge=10,le=100, title="Student's age")]
    department:Optional[str]=None
    CGPA:Annotated[float,Field(...,title="Student's CGPA")]

class Student(StudentCreate):
    @computed_field
    @property
    def id(self) -> str:
        return str(uuid4())
    
    @computed_field  
    @property
    def created_at(self) -> datetime:
        return datetime.now(timezone.utc)

class StudentUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    email:Annotated[Optional[EmailStr],Field(default=None)]
    age: Annotated[Optional[int],Field(default=None, ge=10,le=100)]
    department:Optional[str]=None
    CGPA:Annotated[Optional[float],Field(default=None)]


app=FastAPI()

def load_data():
    with open("students_miniproject.json","r") as f:
        data=json.load(f)
        return data
    
# to save python dict data into json file 
def save_data(data):
    with open("students_miniproject.json","w") as f:
        json.dump(data,f,default=str) 


#List All Students → Show all students from the JSON file.
@app.get("/students")
def get_students_data():
    data=load_data()
    return data

#Get Student by ID → Retrieve details of a student by their ID.
@app.get("/student/{student_id}")
def get_student_data(student_id:str=Path(...,description="The id of the student")):
    data=load_data()

    if student_id in data:
        return data[student_id]
    raise HTTPException(status_code=404,detail="Student not found")

#Create Student → Add a new student to the JSON file.
@app.post('/create_student')
def create_student(student: StudentCreate):
    data=load_data()

    
    # check if email already exists
    for sid,info in data.items():
        if info['email'] == student.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    new_student = Student(**student.model_dump())
    student_dict = new_student.model_dump(mode="json")
    student_id = student_dict.pop("id")
    data[student_id] = student_dict

    save_data(data)

    return JSONResponse(status_code=201, content={"message":"Student created successfully"})

#Delete Student → Remove a student from the JSON file.
@app.delete('/student/{student_id}')
def delete_student(student_id:str):
    data=load_data()

    if student_id not in data:
        raise HTTPException(status_code=404,detail="Student not found")
    
    del data[student_id]

    save_data(data)

    return JSONResponse(status_code=200,content={"message":"Student deleted successfully"})

#Update Student → Edit student information (e.g., name, age, email, department)
@app.put('/student/{student_id}')
def update_student(student_id: str, student_update: StudentUpdate = Body(...)):
    data = load_data()

    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get existing student
    existing_student_info = data[student_id]

    # Only update fields provided in request
    updated_fields = student_update.model_dump(exclude_unset=True)
    for key, value in updated_fields.items():
        existing_student_info[key] = value

    # Save back
    data[student_id] = existing_student_info
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Student updated successfully"})


#Search by name or email.
@app.get('/students/search')
def get_student_data_by_name_or_email(student_name_or_email:str=Query(...,description="The name or email of the student")):
    data=load_data()

    result=[]
    for student_id,student in data.items():
        if student_name_or_email.lower() in student.get("name") or student_name_or_email.lower() in student.get("email"):
            result.append({**student, "id": student_id})

    if not result:
        raise HTTPException(status_code=404,detail="Student not found")
    
    return result 

#Filter by department.
@app.get("/students/filter")
def filter_students(department: str = Query(..., description="Department to filter")):
    data = load_data()
    
    result = []

    for student_id, student in data.items():
        if student["department"].lower() == department.lower():
            result.append({**student, "id": student_id})

    if not result:
        raise HTTPException(status_code=404, detail="No students found in this department")

    return result



#Sorting students by age or name.
@app.get("/sort")
def get_sorted_data(sort_by:str=Query(...,description="Sort by age or name"),order:str=Query("asc",description="Sort in asc or desc order")):
    
    allowed_sorting=['name','age']
    if sort_by not in allowed_sorting:
        raise HTTPException(status_code=400,detail="Sorting by name and age allowed only")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400, detail="Sort in ascending or descending order")
    
    data=load_data()

    sort_order=True if order=="desc" else False
    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)
    return sorted_data



#A simple stats endpoint → total students, average age, count per department.
@app.get("/students/stats")
def get_student_stats():
    data = load_data()
    
    total_students = len(data)
    
    if total_students == 0:
        return {
            "total_students": 0,
            "average_age": 0,
            "count_per_department": {}
        }

    # Calculate average age
    total_age = sum(student.get("age", 0) for student in data.values())
    average_age = total_age / total_students

    # Count per department
    count_per_department = defaultdict(int)
    for student in data.values():
        dept = student.get("department")
        count_per_department[dept] += 1

    # Convert defaultdict to normal dict
    count_per_department = dict(count_per_department)

    return {
        "total_students": total_students,
        "average_age": average_age,
        "count_per_department": count_per_department
    }
