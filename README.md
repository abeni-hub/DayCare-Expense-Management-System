# Recipe App API 🍲

A **production-ready RESTful Recipe API** designed for managing recipes, ingredients, and users.
This project follows **industry best practices**, including **Dockerized development**, **PostgreSQL integration**, **Swagger API documentation**, **automated testing**, **linting with Flake8**, and **CI/CD using GitHub Actions**.

---

## 🚀 Features

* RESTful API for recipe management
* User authentication and authorization
* CRUD operations for recipes and ingredients
* PostgreSQL as the primary database
* Docker & Docker Compose for containerized development
* Swagger UI (OpenAPI) for interactive API documentation
* Unit and integration testing
* Code quality enforcement using Flake8
* Automated CI/CD pipeline with GitHub Actions
* Environment-based configuration

---

## 🛠️ Tech Stack

* **Backend:** Django & Django REST Framework
* **Database:** PostgreSQL
* **API Documentation:** Swagger UI (OpenAPI)
* **Containerization:** Docker, Docker Compose
* **Testing:** Django Test Framework (Unit & Integration Tests)
* **Linting:** Flake8
* **CI/CD:** GitHub Actions
* **Version Control:** Git & GitHub

---

## 🏗️ Project Architecture

```
recipe-app-api/
├── app/
│   ├── core/          # Core models and utilities
│   ├── user/          # User authentication & management
│   ├── recipe/        # Recipe and ingredient features
│   ├── tests/         # Unit & integration tests
│   └── manage.py
├── .github/
│   └── workflows/
│       └── ci.yml     # CI pipeline (tests, linting)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .flake8
├── .env.example
└── README.md
```

---

## 🐳 Docker Setup (Local Development)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/recipe-app-api.git
cd recipe-app-api
```

### 2️⃣ Build and start containers

```bash
docker-compose build
docker-compose up
```

### 3️⃣ Run database migrations

```bash
docker-compose run --rm app python manage.py migrate
```

### 4️⃣ Create a superuser

```bash
docker-compose run --rm app python manage.py createsuperuser
```

The API will be available at:

```
http://localhost:8000
```

---

## 📘 API Documentation (Swagger UI)

Interactive API documentation is available via **Swagger UI**:

```
http://localhost:8000/api/docs/
```

Features:

* Endpoint exploration
* Request/response schemas
* Authentication testing directly from the browser

---

## 🧪 Testing Strategy

This project includes **multiple levels of testing**:

* **Unit Tests:**
  Test individual models, serializers, and utility functions

* **Integration Tests:**
  Test API endpoints, database interactions, and authentication flows

### Run tests

```bash
docker-compose run --rm app python manage.py test
```

---

## 🧹 Linting with Flake8

Code quality is enforced using **Flake8** to ensure:

* PEP8 compliance
* Clean, readable, maintainable code

### Run linting

```bash
docker-compose run --rm app flake8
```

---

## 🔁 CI/CD Pipeline (GitHub Actions)

The GitHub Actions workflow automatically runs on:

* Every **push**
* Every **pull request**

### CI Pipeline includes:

* Flake8 linting
* Unit & integration tests
* Docker build validation

This ensures **high-quality, production-safe code** before merging.

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=1
SECRET_KEY=your-secret-key

DB_NAME=recipe
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

---

## 📈 Future Enhancements

* Role-based access control (RBAC)
* API rate limiting
* Redis caching
* Production deployment with Nginx & Gunicorn
* Monitoring and logging integration

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Ab**
Backend Developer | Django REST Framework
GitHub: (https://github.com/abeni-hub)

---

⭐ Star this repository if you find it helpful!
