# FastAPI Project

This is a simple FastAPI project that interacts with a MySQL database.

## Description

This project demonstrates how to create a RESTful API using FastAPI to perform basic CRUD operations on a MySQL database.

## Requirements

- Python 3.x
- FastAPI
- uvicorn
- mysql-connector-python

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Marwan-Gama/saints-app.git
   ```

2. Install the dependencies:
   ```bash
   pip install fastapi uvicorn mysql-connector-python
   ```

## Usage

1. Configure your MySQL connection in config.py.
2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
3. Access the API documentation at http://localhost:8000/docs.

## Endpoints

/: Homepage.
/data: Fetch all customer data.
/saints: Fetch all saints.
/who?name={name}: Fetch customer by name.
/saints (POST): Add a new saint.
/short-desc: Fetch a short description of customers.
/admin/saint/age/{min_age}/{max_age}: Fetch saints within a specific age range.
/admin/notsaint/age/{min_age}/{max_age}: Fetch non-saints within a specific age range.
/admin/name/{search_name}: Fetch saints by name.
/admin/average: Fetch average ages of saints and non-saints.

## This project is created by [Marwan Abu Gama].
