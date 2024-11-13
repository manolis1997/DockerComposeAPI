from fastapi import FastAPI
from pydantic import BaseModel
import pyodbc
from typing import List, Dict
import uvicorn
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()
encrypted_password = os.getenv("SQL_SERVER_PASS")

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER=host.docker.internal,1433;'
        f'UID=sa;'
        f'PWD={encrypted_password};'
        f'Trusted_Connection=no;'
    )
    return conn


class DataModel(BaseModel):
    Department: str
    Name: str
    ID_str: str
    Salary_str: str


@app.get("/data", response_model=Dict[str, List[Dict[str, str]]])
async def read_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Department, Name, CAST(ID AS VARCHAR(10)) AS ID_str, CAST(Salary AS VARCHAR(10)) AS Salary_str FROM Employee")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create a dictionary where each department is the key and the value is a list of employees in that department
    result = {}
    for row in data:
        department = row[0]
        employee = {"dept": row[0], "name": row[1], "id_str": row[2], "salary": row[3]}  # Adjust this as needed
        if department not in result:
            result[department] = []
        result[department].append(employee)

    return result

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=3000)
    get_db_connection().close()
