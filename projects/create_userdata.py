import csv
import random
import string
from faker import Faker
# Initialize Faker
fake = Faker()

# Generate random email and password pairs
def generate_email_password_pairs(n):
    pairs = []
    for _ in range(n):
        email = fake.user_name() + "@gmail.com"
        password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=random.randint(9, 16)))
        pairs.append((email, password))
    return pairs

# Generate 100 pairs
data = generate_email_password_pairs(1000)

# File path
file_path = "users.csv"

# Write to CSV file
with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["email", "password"])  # Header
    writer.writerows(data)

file_path
