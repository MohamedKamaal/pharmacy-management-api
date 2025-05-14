Pharmacy Management System
Project Description
The Pharmacy Management System is a web application designed to manage the daily operations of a pharmacy. It enables pharmacists to manage medicines, process orders, track inventory, and manage stock levels (including expired and near-expiry medicines) ,cashiers to handle sales invoices. The system also supports the return of invoices and refunds.

Tech Stack
Backend: Django, Django REST Framework (DRF)

Database: PostgreSQL

Authentication: JWT (JSON Web Token) for token-based authentication

API Documentation: Swagger/Redoc 

Other Libraries:

django-filter for filtering querysets

django-cors-headers for cross-origin requests

dateutil.relativedelta for date manipulations

Setup Instructions
Installation
Clone the repository:



git clone https://github.com/your-username/pharmacy-management.git
cd pharmacy-management
Set up a virtual environment and install dependencies:



python3 -m venv env
source env/bin/activate   # On Windows, use `env\Scripts\activate`
pip install -r requirements.txt
Set up environment variables (create a .env file):



DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
Run database migrations:



python manage.py migrate
Create a superuser for the Django admin panel:



python manage.py createsuperuser
Run the server:



python manage.py runserver
Now the app should be running at http://localhost:8000/.

Environment
Ensure you have Python 3.8+ and PostgreSQL installed. You'll need to configure PostgreSQL to create the database and user as per the .env configuration.

Usage
Running the Project
To run the development server:



python manage.py runserver
You can now access the API at http://localhost:8000/. The admin panel is available at http://localhost:8000/admin/.

Endpoints Overview
Sales Endpoints
GET /api/invoices/ – List paid invoices (restricted to cashiers)

POST /api/invoices/ – Create a new invoice

POST /api/invoices/return/ – Refund an invoice (mark as refunded)

Orders Endpoints
GET /api/orders/ – List all orders (restricted to pharmacists)

POST /api/orders/ – Create a new order

Medicines Endpoints
GET /api/medicines/ – List and search medicines (with filtering and pagination)

POST /api/medicines/ – Add a new medicine

GET /api/medicines/{id}/similar/ – Get similar medicines by active ingredient and category

GET /api/medicines/{id}/batches/ – List all batches for a specific medicine

Stock Management Endpoints
GET /api/stock/out-of-stock/ – List out-of-stock batches

GET /api/stock/expired/ – List expired batches

GET /api/stock/near-expiry/?months=2 – List batches expiring within 2 months (parameterized)

Authentication
This application uses JWT (JSON Web Token) for authentication.

Login Endpoint: POST /api/token/
Send your username and password to receive an access token and refresh token.

Protected Endpoints: All endpoints except login and registration are protected and require a valid JWT token in the Authorization header:
Authorization: Bearer <your-access-token>

Testing
To run tests, follow these steps:

Install test dependencies:



pip install -r requirements-test.txt
Run the tests:



python manage.py test
This will run all the tests defined in your tests/ folder.

Contributors / License
Contributors
Your Name – GitHub Profile

License
This project is licensed under the MIT License – see the LICENSE file for details.
Demo 
http://13.42.86.160/
