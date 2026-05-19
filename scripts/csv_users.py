import csv

PASSWORD = "Test1234"
NUM_USERS = 1000
CSV_FILE = "users.csv"

with open(CSV_FILE, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["email", "password"])  # header

    for i in range(1, NUM_USERS + 1):
        email = f"test_user_{i}@test.com"
        writer.writerow([email, PASSWORD])

print(f"CSV generado: {CSV_FILE}")