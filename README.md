# Django REST & GraphQL API – Diploma Project

**Author:** Volodymyr Yurasov  
**Student Group:** FEI-42  
**University:** Ivan Franko National University of Lviv

This repository contains the code for a diploma project that implements both REST and GraphQL APIs using Django. The project supports API testing, user interaction, project execution with restricted Python code evaluation, and token-based authentication.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone git@github.com:MusicW0lf/django-restApi13.git
cd django-restApi13
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# Activate it:
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🖥️ Running the Server

```bash
waitress-serve --listen=0.0.0.0:8080 --threads=32 server.wsgi:application
```

- **REST API:** [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- **GraphQL API:** [http://127.0.0.1:8080/graphql](http://127.0.0.1:8080/graphql)

---

## 📌 API Endpoints (REST)

> All endpoints requiring authentication use JWT via HttpOnly cookies.

| Method | Path                                      | Description |
|--------|-------------------------------------------|-------------|
| POST   | `/signup`                                 | Register a new user |
| POST   | `/login`                                  | Authenticate a user and set JWT cookie |
| POST   | `/logout`                                 | Log out and clear authentication cookie |
| GET    | `/user-details`                           | Retrieve the authenticated user's username |
| GET    | `/user-projects/`                         | List all projects owned by the current user |
| POST   | `/create-project`                         | Create a new project (requires `name`, `language`) |
| GET    | `/project/<project_id>/`                  | Get project data (only if user is the author) |
| DELETE | `/project/<project_id>/delete/`           | Delete a project (only by the author) |
| PATCH  | `/project/<project_id>/rename/`           | Rename an existing project (only by the author) |
| POST   | `/project/execute/`                       | Save and execute restricted Python code in a project |

---

## 🧪 Load Testing with Locust

Navigate to the `projects` directory to run performance tests:

### Run GraphQL Load Tests

```bash
locust -f locust_graphql.py --host=http://127.0.0.1:8080/graphql/
```

### Run REST Load Tests

```bash
locust -f locust_rest.py --host=http://127.0.0.1:8080/
```

---

## 🔐 Authentication

- Authentication is based on JWT tokens stored in HttpOnly cookies.
- Login and signup endpoints issue the token and set it in the browser.
- All protected endpoints require a valid token in the cookie.

---

## 🧠 Project Execution Feature

The `/project/execute/` endpoint allows users to safely run Python code inside a restricted environment (sandboxed using `RestrictedPython`). Output is captured and returned as a list of printed lines.

---

## 📄 License

This project was developed as part of a diploma thesis and is intended for educational use.
