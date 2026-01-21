# 🏫 DayCare Expense Management System – Backend (Django REST Framework)

A robust **backend application** built with **Django & Django REST Framework (DRF)** to support the **DayCare Expense Management System**, seamlessly integrated with a **React + TypeScript frontend**. This backend ensures **secure, accurate, and scalable financial data management** for DayCare operations.

---

## 📌 Project Overview

The **DayCare Expense Management Backend** provides a RESTful API for managing all expense-related data used by the frontend application. It handles:

* Expense and expense-item management
* VAT calculation and validation
* Category, supplier, and payment source tracking
* Pagination and filtering
* Secure integration with a React + TypeScript frontend

The backend is designed with **clean architecture**, **data integrity**, and **API-first development** principles.

---

## 🛠️ Tech Stack

### Backend

* **Python**
* **Django** – Core web framework
* **Django REST Framework (DRF)** – RESTful API development
* **PostgreSQL / SQLite** – Database (configurable)
* **Django ORM** – Database modeling & queries

### Frontend Integration

* **React + TypeScript**
* **Redux Toolkit & RTK Query** for API consumption
* JSON-based REST communication

---

## 🔗 Frontend–Backend Integration

The backend exposes **RESTful endpoints** consumed by the React frontend using **RTK Query**. The API provides:

* Consistent response formats
* Pagination (`count`, `next`, `previous`)
* Validation and error handling
* Strong compatibility with TypeScript interfaces

### Example API Response

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "items": [
        {
          "id": 3,
          "item_name": "Marker",
          "quantity": "5.00",
          "unit": "pcs",
          "unit_price": "30.00",
          "total": "150.00"
        }
      ],
      "date": "2026-01-17",
      "description": "Office supplies UPDATED",
      "category": "Stationery",
      "supplier": "Local Shop",
      "payment_source": "cash",
      "vat_enabled": false,
      "vat_rate": "15.00",
      "vat_amount": "0.00",
      "total_expense": "150.00",
      "remarks": "Bought pens and papers",
      "created_at": "2026-01-17T07:29:40.091268Z"
    }
  ]
}
```

---

## 📁 Backend Project Structure

```text
backend/
│── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
│── expenses/
│   ├── models.py        # Expense & ExpenseItem models
│   ├── serializers.py   # DRF serializers
│   ├── views.py         # API views / viewsets
│   ├── urls.py          # App-level routes
│   └── admin.py
│
│── manage.py
```

---

## 🧩 Core Features

### 1️⃣ Expense & Item Management

* Create, update, retrieve, and delete expenses
* Support for multiple items per expense
* Server-side total calculations

### 2️⃣ VAT Handling

* VAT enable/disable per expense
* Configurable VAT rate
* Automatic VAT amount calculation

### 3️⃣ Data Validation & Integrity

* Serializer-level validation
* Accurate decimal handling for financial values
* Prevents inconsistent or invalid data

### 4️⃣ Pagination & Filtering

* DRF pagination support
* Efficient querying for large datasets

---

## 🔐 Authentication & Security (Optional)

* Token / JWT authentication
* Permission-based access control
* Secure API endpoints for authorized users only

---

## ⚙️ Environment Configuration

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/daycare_db
```

---

## ▶️ Running the Backend Project

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

---

## 🔄 Integration Workflow

1. Backend exposes REST APIs via DRF
2. React + TypeScript frontend consumes APIs using RTK Query
3. TypeScript interfaces mirror backend serializers
4. Backend ensures validation and persistence

---

## 🎯 Design Principles

* **API-First Development**
* **Scalability** for growing DayCare data
* **Security & Accuracy** for financial records
* **Separation of Concerns** between frontend and backend

---

## 🚀 Future Enhancements

* Advanced reporting & analytics endpoints
* Role-based access control (Admin, Accountant)
* Audit logs for expense changes
* Multi-DayCare / branch support

---

## 📄 License

This backend is developed for **DayCare Expense Management** and intended for controlled or licensed use.

---

### ✅ Summary

The **Django REST Framework backend** provides a **secure, scalable, and reliable foundation** for the DayCare Expense Management System, tightly integrated with a **React + TypeScript frontend** to deliver a complete end-to-end solution.

---

📌 *Built to ensure accuracy, reliability, and seamless frontend integration for DayCare expense tracking.*
