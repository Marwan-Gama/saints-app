from typing import List, Union
from fastapi import Body, Depends, FastAPI, HTTPException, Query,Path
import mysql.connector
from mysql.connector import Error
from fastapi.responses import HTMLResponse
from config import connection_config
from pydantic import BaseModel

app = FastAPI()

# Establish MySQL connection
connection = mysql.connector.connect(**connection_config)

if connection.is_connected():
    print("Connected to MySQL database")
else:
    print("Failed to connect to MySQL database")

current_username = "name"

def username_is_admin(username):
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT isAdmin FROM customers WHERE name = %s", (username,)
        )
        result = cursor.fetchone()
        if result and result[0]:
            return True
        else:
            raise HTTPException(
                status_code=403, detail="User is not an admin"
            )
    except Error as e:
        print("Error checking admin status:", e)
        raise HTTPException(
            status_code=500, detail="Internal Server Error"
        )
    finally:
        if "cursor" in locals():
            cursor.close()


class Customer(BaseModel):
    id: int
    name: str
    age: int
    occupation_name: str
    isSaint: bool
    password: str
    isAdmin: bool

class LoginDetails(BaseModel):
    username: str
    password: str



@app.post("/login")
async def login(login_details: LoginDetails = Body(...)):
    global current_username
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE name = %s AND password = %s", (login_details.username, login_details.password))
        customer = cursor.fetchone()
        current_username = login_details.username
        if customer:
            # If the customer exists in the database and the password matches
            return {"message": "Login successful"}
        else:
            # If the customer does not exist in the database or the password does not match
            raise HTTPException(status_code=401, detail="Unauthorized")
    except Error as e:
        print("Error during login:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if 'cursor' in locals():
            cursor.close()


@app.get("/")
async def index():
    return "Ahalan! You can fetch some json by navigating to '/json'"

@app.get("/data", response_model=List[Customer])
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
                "isSaint": bool(customer[4]),
                "password": customer[5],
                "isAdmin": bool(customer[6])
            }
            customers_list.append(Customer(**customer_dict))
        return customers_list
    except Error as e:
        print("Error retrieving customer data from MySQL database:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve customer data from database")
    finally:
        if 'cursor' in locals():
            cursor.close()


@app.get("/saints", response_model=List[Customer])
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
                "isSaint": bool(saint[4]),
                "password": saint[5],
                "isAdmin": bool(saint[6])
            }
            saint_list.append(Customer(**saint_dict))
        return saint_list
    except Error as e:
        print("Error retrieving saints from MySQL database:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve saints from database")
    finally:
        if 'cursor' in locals():
            cursor.close()


@app.get("/who", response_model=Union[Customer, str])
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
async def add_saint(saint: Customer):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO customers (id, name, age, occupation_name, isSaint, password, isAdmin) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (saint.id, saint.name, saint.age, saint.occupation_name, saint.isSaint, saint.password, saint.isAdmin))
        connection.commit()
        print("Saint added successfully to MySQL database")
        return {"message": "Saint added successfully"}
    except Error as e:
        print("Error inserting data into MySQL table:", e)
        raise HTTPException(status_code=500, detail="Failed to add Saint to database")
    finally:
        if 'cursor' in locals():
            cursor.close()


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


@app.get("/admin/saint/age/{min_age}/{max_age}", response_model=List[Customer])

async def get_saints_in_age_range(min_age: int = Path(..., title="Minimum Age", ge=0), max_age: int = Path(..., title="Maximum Age", ge=0), cursor = Depends(get_cursor)):
    try:
        is_admin = username_is_admin(current_username)
        if is_admin:
            cursor.execute("SELECT * FROM customers WHERE isSaint = 1 AND age BETWEEN %s AND %s", (min_age, max_age))
            saints = cursor.fetchall()
            saint_list = []
            for saint in saints:
                saint_dict = {
                    "id": saint[0],
                    "name": saint[1],
                    "age": saint[2],
                    "occupation_name": saint[3],
                    "isSaint": bool(saint[4]),
                    "password": saint[5],  
                    "isAdmin": bool(saint[6]) 

                }
                saint_list.append(saint_dict)
            return saint_list
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve saints from database")


@app.get("/admin/notsaint/age/{min_age}/{max_age}", response_model=List[Customer])
async def get_notsaints_in_age_range(min_age: int = Path(..., title="Minimum Age", ge=0), max_age: int = Path(..., title="Maximum Age", ge=0), cursor = Depends(get_cursor)):
    try:
        is_admin = username_is_admin(current_username)
        if is_admin:
            cursor.execute("SELECT * FROM customers WHERE isSaint = 0 AND age BETWEEN %s AND %s", (min_age, max_age))
            notsaints = cursor.fetchall()
            notsaint_list = []
            for notsaint in notsaints:
                notsaint_dict = {
                    "id": notsaint[0],
                    "name": notsaint[1],
                    "age": notsaint[2],
                    "occupation_name": notsaint[3],
                    "isSaint": bool(notsaint[4]),
                    "password": notsaint[5],  
                    "isAdmin": bool(notsaint[6]) 

                }
                notsaint_list.append(notsaint_dict)
            return notsaint_list
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve not saints from database")


@app.get("/admin/name/{search_name}", response_model=List[Customer])
async def get_saints_by_name(search_name: str = Path(..., title="Search Name"), cursor = Depends(get_cursor)):
    try:
        is_admin = username_is_admin(current_username)
        if is_admin:
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


@app.get("/admin/average", response_model=Customer)
async def get_average_ages(cursor = Depends(get_cursor)):
    try:
        is_admin = username_is_admin(current_username)
        if is_admin:
            cursor.execute("SELECT AVG(age) FROM customers WHERE isSaint = 1")
            saint_avg_age = cursor.fetchone()[0]
            cursor.execute("SELECT AVG(age) FROM customers WHERE isSaint = 0")
            notsaint_avg_age = cursor.fetchone()[0]
            return {"saint_avg_age": saint_avg_age, "notsaint_avg_age": notsaint_avg_age}
    except Error as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve average ages from database")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
