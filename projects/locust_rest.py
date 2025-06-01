from locust import HttpUser, task, between
import csv
import random
import string
from itertools import cycle
user_credentials = []
with open("users.csv", newline="") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 100:
            break
        user_credentials.append(row)

user_cycle = cycle(user_credentials)


class DjangoUser(HttpUser):
    wait_time = between(1, 10)
    host = "http://0.0.0.0:8080"

    def on_start(self):
        self.project_id = None
        self.user_data = next(user_cycle)
        self.email = self.user_data['email']
        self.username = self.user_data['email']
        self.password = self.user_data['password']
        self.token = 0

        if not self.login():
            self.signup()
            self.login()

    def login(self):
        response = self.client.post(
            "/login",
            json={"email": self.email, "password": self.password, "username": self.username},
            headers={"Content-Type": "application/json"},
            name="Login"
        )
        if response.status_code == 200:
            token = response.cookies.get("access_token")
            if token:
                self.client.cookies.set("access_token", token)
                self.token = token
                return True
        print(f"Login failed for {self.email}")
        return False

    def signup(self):
        response = self.client.post(
            "/signup",
            json={"email": self.email, "password": self.password, "username": self.username},
            headers={"Content-Type": "application/json"},
            name="Signup"
        )
        if response.status_code in [200, 201]:
            token = response.cookies.get("access_token")
            if token:
                self.token = token
                self.client.cookies.set("access_token", token)
        else:
            print(f"Signup failed for {self.email}: {response.text}")

    @task
    def full_user_journey(self):
        self.create_project()
        self.rename_project()
        self.execute_project()
        self.get_projects()
        self.delete_project()

    def create_project(self):
        name = "Project_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        language = "Python"

        response = self.client.post(
            "/create-project",
            json={"name": name, "language": language},
            headers={"Content-Type": "application/json"},
            name="Create Project"
        )

        if response.status_code == 201:
            self.project_id = response.json().get("project_id")
        else:
            if not self.token:
                print(f"Create failed for {self.email}: {response.text}")
                self.login()
            else:
                print("Fail not because of token", response.text)

    def rename_project(self):
        if not self.project_id:
            return
        new_name = "Project_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        response = self.client.patch(
            f"/project/{self.project_id}/rename/",
            json={"name": new_name},
            headers={"Content-Type": "application/json"},
            name="Rename Project"
        )
        if response.status_code != 200:
            if not self.token:
                print(f"Rename failed for {self.email}: {response.text}")
                self.login()
            else:
                print("Fail not because of token", response.text)

    def execute_project(self):
        if not self.project_id:
            return
        code = "print(123*123)"
        response = self.client.post(
            "/project/execute/",
            json={"code": code, "project_id": self.project_id},
            headers={"Content-Type": "application/json"},
            name="Execute Project"
        )
        if response.status_code != 200:
            if not self.token:
                print(f"Execute failed for {self.email}: {response.text}")
                self.login()
            else:
                print("Fail not because of token", response.text)

    def get_projects(self):
        response = self.client.get("/user-projects/", name="Get Projects")

        if response.status_code != 200:
            if not self.token:
                print(f"Get projects failed for {self.email}: {response.text}")
                self.login()
            else:
                print("Fail not because of token", response.text)


    def delete_project(self):
        if not self.project_id:
            return
        response = self.client.delete(
            f"/project/{self.project_id}/delete/",
            headers={"Content-Type": "application/json"},
            name="Delete Project"
        )
        if response.status_code == 204:
            self.project_id = None
        else:
            if not self.token:
                print(f"Deletion failed for {self.email}: {response.text}")
                self.login()
            else:
                print("Fail not because of token", response.text)

