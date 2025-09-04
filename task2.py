from fastapi import FastAPI, Path, HTTPException,Query
import json

app=FastAPI()

def load_data():
    with open("students.json","r") as f:
        data=json.load(f)
        return data
    
@app.get("/view")
def get_students_data():
    data=load_data()
    return data

@app.get("/student/{student_id}")
#..., means required, its required by default tho
def get_student_data(student_id:str=Path(...,description="The id of the student", example="S001")):
    data=load_data()

    if student_id in data:
        return data[student_id]
    raise HTTPException(status_code=404,detail="Student not found")

@app.get("/sort")
def get_sorted_data(sort_by:str=Query(...,description="Sort by CGPA"),order:str=Query("asc",description="Sort in asc or desc order")):

    if sort_by != "CGPA":
        raise HTTPException(status_code=400,detail="Sorting by CGPA allowed only")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=200, detail="Sort in ascending or descending order")
    
    data=load_data()

    sort_order=True if order=="desc" else False
    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)
    return sorted_data
