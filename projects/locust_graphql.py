from locust import HttpUser, task, between
import csv
import random
import string
from itertools import cycle

user_credentials = []
with open("users.csv", newline="") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 1000:
            break
        user_credentials.append(row)

user_cycle = cycle(user_credentials)

def graphql_query(query, variables=None):
    return {
        "query": query,
        "variables": variables or {}
    }

class GraphQLUser(HttpUser):
    wait_time = between(1, 10)
    host = "http://127.0.0.1:8080/graphql/"


    def on_start(self):
        self.project_id = None
        self.user_data = next(user_cycle)
        self.email = self.user_data['email']
        self.username = self.user_data['email']
        self.password = self.user_data['password']
        self.token = None

        if not self.login():
            self.signup()
            self.login()

    def login(self):
        response = self.client.post(
            "http://127.0.0.1:8080/login",
            json={"email": self.email, "password": self.password, "username": self.username},
            headers={"Content-Type": "application/json"},
            name=None
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
            "http://127.0.0.1:8080/signup",
            json={"email": self.email, "password": self.password, "username": self.username},
            headers={"Content-Type": "application/json"},
            name=None
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
        language = "PYTHON"

        query = """
            mutation CreateProject($name: String!, $language: String!) {
                createProject(name: $name, language: $language) {
                    project {
                        projectId
                        name
                        language
                    }
                }
            }
        """

        variables = {"name": name, "language": language}

        response = self.client.post(
            "",
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            name="Create Project"
        )

        if response.status_code != 200:
            print(f"Create project failed ({response.status_code}): {response.text}")
            return

        try:
            json_response = response.json()
        except ValueError:
            print(f"Invalid JSON response: {response.text}")
            return

        if "errors" in json_response:
            print(f"GraphQL errors during createProject: {json_response['errors']}")
            return

        project_data = (
            json_response
            .get("data", {})
            .get("createProject", {})
            .get("project")
        )

        if project_data and "projectId" in project_data:
            self.project_id = project_data["projectId"]  # Note: still a string
        else:
            print(f"Create project failed: Unexpected response format: {json_response}")


    def rename_project(self):
        if not self.project_id:
            return
        new_name = "Renamed_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        mutation = """
        mutation RenameProject($projectId: Int!, $name: String!) {
            renameProject(projectId: $projectId, name: $name) {
                project {
                    name
                }
            }
        }
        """
        response = self.client.post("", json=graphql_query(mutation, {
            "projectId": int(self.project_id),
            "name": new_name
        }), name="Rename Project")
        if response.status_code != 200:
            print(f"Rename failed: {response.text}")

    def execute_project(self):
        if not self.project_id:
            return
        mutation = """
        mutation ExecuteCode($projectId: Int!, $code: String!) {
            executeCode(projectId: $projectId, code: $code) {
                stdout
                error
            }
        }
        """
        response = self.client.post("", json=graphql_query(mutation, {
            "projectId": int(self.project_id),
            "code": "print(123*123)"
        }), name="Execute Project")
        if response.status_code != 200:
            print(f"Execute failed: {response.text}")

    def get_projects(self):
        query = """
        query {
            myProjects {
                projectId
                name
            }
        }
        """
        response = self.client.post("", json=graphql_query(query), name="Get Projects")
        if response.status_code != 200:
            print(f"Get projects failed: {response.text}")

    def delete_project(self):
        if not self.project_id:
            return
        mutation = """
        mutation DeleteProject($projectId: Int!) {
            deleteProject(projectId: $projectId) {
                success
            }
        }
        """
        response = self.client.post("", json=graphql_query(mutation, {
            "projectId": int(self.project_id)
        }), name="Delete Project")
        if response.status_code == 200:
            self.project_id = None
        else:
            print(f"Deletion failed: {response.text} response: {response.text}")
