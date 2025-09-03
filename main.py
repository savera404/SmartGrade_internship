from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def hello():
    return {"message":"Hello World"}

@app.get("/student")
def get_student_info():
    return {"message":{"Name": "Savera Rizwan", "Id":"SE-22022", "Field":"Software Engineering"}}