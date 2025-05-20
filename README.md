
# 💊 Pharmacy Management REST API

A robust, scalable RESTful API built with Django and Django REST Framework for managing pharmacy operations — including medicine inventory, orders, sales, user authentication, and reporting.

---

## 🚀 Features

- **User Authentication & Authorization**
  - JWT cookie-based auth (via `dj-rest-auth`)
  - Email-based registration (custom user model)
  - Role-based access control
- **Medicine Management**
  - Medicines, Batches, Manufacturers, Suppliers, Active Ingredients
  - Category hierarchy using MPTT
- **Orders & Sales**
  - Order creation and management
  - Invoice generation & returns
- **Reports**
  - Sales and inventory reporting (custom endpoints)
- **Geo Support**
  - Egyptian cities via `django-cities-light`
- **API Documentation**
  - Swagger via `drf_yasg`

---## 🧱 Tech Stack

- **Framework**: Django 5.x, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (via `dj-rest-auth`)
- **Others**:
  - `django-allauth`, `mptt`, `django-countries`, `django-cities-light`
  - Logging & error handling
  - Whitenoise for static file serving

---

## Demo
live demo http://13.42.86.160/


## 🧱 Apps Structure

| App        | Responsibility                                       |
|------------|------------------------------------------------------|
| `users`    | Custom user model & manager, profile logic          |
| `store`    | Products, categories, product variations             |
| `cart`     | Cart logic and views (add, remove, update, total)   |
| `orders`   | Order creation, confirmation, and tracking          |
| `payments` | Stripe integration and payment verification         |
| `shipping` | Shipping address and delivery info forms            |
| `reviews`  | Product reviews and ratings                         |

## Deployment

Deployed on aws ec2
## Installation

Follow these steps to get the project running locally:

### 1. Clone the repository

```bash
git clone https://github.com/MohamedKamaal/pharmacy-management-api.git
cd blog
pip install -r requirements.txt
```

### 2. Apply database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
### 3. Run the development server
```bash
python manage.py runserver
```
### 4. Access API documentation
```bash
http://localhost:8000/redoc/
```
## Running Tests

To run tests, run the following command

```bash
  pytest 
```
