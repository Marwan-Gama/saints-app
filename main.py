from typing import List
from fastapi import Depends, FastAPI, HTTPException, Query,Path
import mysql.connector
from mysql.connector import Error
from fastapi.responses import HTMLResponse
from config import connection_config

app = FastAPI()

# Establish MySQL connection
connection = mysql.connector.connect(**connection_config)

if connection.is_connected():
    print("Connected to MySQL database")
else:
    print("Failed to connect to MySQL database")



@app.get("/")
async def index():
    return "Ahalan! You can fetch some json by navigating to '/json'"

@app.get("/data")
async def get_data():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers")
        customers_data = cursor.fetchall()
        customers_list = []
        for customer in customers_data:
            customer_dict = {
                "id": customer[0],
                "name": customer[1],
                "age": customer[2],
                "occupation_name": customer[3],
                "isSaint": bool(customer[4])
            }
            customers_list.append(customer_dict)
        return customers_list
    except Error as e:
        print("Error retrieving customer data from MySQL database:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve customer data from database")
    finally:
        if 'cursor' in locals():
            cursor.close()


@app.get("/saints")
async def get_saints():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE isSaint = 1")
        saints = cursor.fetchall()
        saint_list = []
        for saint in saints:
            saint_dict = {
                "id": saint[0],
                "name": saint[1],
                "age": saint[2],
                "occupation_name": saint[3],
                "isSaint": bool(saint[4])
            }
            saint_list.append(saint_dict)
        return saint_list
    except Error as e:
        print("Error retrieving saints from MySQL database:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve saints from database")
    finally:
        if 'cursor' in locals():
            cursor.close()


@app.get("/who")
async def get_customer(name: str = Query(None, min_length=2, max_length=11)):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE name = %s", (name,))
        customer = cursor.fetchone()
        if customer:
            customer_dict = {
                "id": customer[0],
                "name": customer[1],
                "age": customer[2],
                "occupation_name": customer[3],
                "isSaint": bool(customer[4])
            }
            return customer_dict
        else:
            return "No such customer"
    except Error as e:
        print("Error retrieving customer from MySQL database:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve customer from database")
    finally:
        if 'cursor' in locals():
            cursor.close()


@app.post("/saints")
async def add_saint(saint: dict):
    if saint:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO customers (id, name, age, occupation_name, isSaint) 
                VALUES (%s, %s, %s, %s, %s)
            """, (saint['id'], saint['name'], saint['age'], saint['occupation']['name'], saint['occupation']['isSaint']))
            connection.commit()
            print("Saint added successfully to MySQL database")
            return {"message": "Saint added successfully"}
        except Error as e:
            print("Error inserting data into MySQL table:", e)
            raise HTTPException(status_code=500, detail="Failed to add Saint to database")
        finally:
            if 'cursor' in locals():
                cursor.close()
    else:
        raise HTTPException(status_code=400, detail="Invalid Saint data")


@app.get("/short-desc", response_class=HTMLResponse)
async def get_short_desc():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name, occupation_name, id FROM customers")
        customers_data = cursor.fetchall()
        html_content = "<html><head><title>Customer Short Description</title></head><body><table border='1'><tr><th>Name</th><th>Occupation</th><th>ID</th></tr>"
        for customer in customers_data:
            html_content += f"<tr><td><a href='/who?name={customer[0]}'>{customer[0]}</a></td><td>{customer[1]}</td><td>{customer[2]}</td></tr>"
        html_content += "</table></body></html>"
        return html_content
    except Error as e:
        print("Error retrieving customer data from MySQL database:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve customer data from database")
    finally:
        if 'cursor' in locals():
            cursor.close()

def get_cursor():
    return connection.cursor()


@app.get("/admin/saint/age/{min_age}/{max_age}", response_model=List[dict])
async def get_saints_in_age_range(min_age: int = Path(..., title="Minimum Age", ge=0), max_age: int = Path(..., title="Maximum Age", ge=0), cursor = Depends(get_cursor)):
    try:
        cursor.execute("SELECT * FROM customers WHERE isSaint = 1 AND age BETWEEN %s AND %s", (min_age, max_age))
        saints = cursor.fetchall()
        saint_list = []
        for saint in saints:
            saint_dict = {
                "id": saint[0],
                "name": saint[1],
                "age": saint[2],
                "occupation_name": saint[3],
                "isSaint": bool(saint[4])
            }
            saint_list.append(saint_dict)
        return saint_list
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve saints from database")


@app.get("/admin/notsaint/age/{min_age}/{max_age}", response_model=List[dict])
async def get_notsaints_in_age_range(min_age: int = Path(..., title="Minimum Age", ge=0), max_age: int = Path(..., title="Maximum Age", ge=0), cursor = Depends(get_cursor)):
    try:
        cursor.execute("SELECT * FROM customers WHERE isSaint = 0 AND age BETWEEN %s AND %s", (min_age, max_age))
        notsaints = cursor.fetchall()
        notsaint_list = []
        for notsaint in notsaints:
            notsaint_dict = {
                "id": notsaint[0],
                "name": notsaint[1],
                "age": notsaint[2],
                "occupation_name": notsaint[3],
                "isSaint": bool(notsaint[4])
            }
            notsaint_list.append(notsaint_dict)
        return notsaint_list
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve not saints from database")


@app.get("/admin/name/{search_name}", response_model=List[dict])
async def get_saints_by_name(search_name: str = Path(..., title="Search Name"), cursor = Depends(get_cursor)):
    try:
        cursor.execute("SELECT * FROM customers WHERE isSaint = 1 AND name LIKE %s", (f"%{search_name}%",))
        saints = cursor.fetchall()
        saint_list = []
        for saint in saints:
            saint_dict = {
                "id": saint[0],
                "name": saint[1],
                "age": saint[2],
                "occupation_name": saint[3],
                "isSaint": bool(saint[4])
            }
            saint_list.append(saint_dict)
        return saint_list
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve saints from database")


@app.get("/admin/average", response_model=dict)
async def get_average_ages(cursor = Depends(get_cursor)):
    try:
        cursor.execute("SELECT AVG(age) FROM customers WHERE isSaint = 1")
        saint_avg_age = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(age) FROM customers WHERE isSaint = 0")
        notsaint_avg_age = cursor.fetchone()[0]
        return {"saint_avg_age": saint_avg_age, "notsaint_avg_age": notsaint_avg_age}
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve average ages from database")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
