import csv
import os
user_credentials = []
with open("users.csv", newline="") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 100:
            break
        print(row)