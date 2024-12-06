import os
import csv
from datetime import datetime

def handle_user_csv(user_id, user_name, link, created_at):
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    csv_filename = os.path.join(data_dir, f"{user_id}.csv")

    # Create CSV if not exists with headers
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "user_id", "user_name", "link", "created_at"
            ])

    # Append user data
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            user_id, user_name, link, created_at
        ])

def get_user_submissions(user_id):
    csv_filename = os.path.join("data", f"{user_id}.csv")

    if not os.path.exists(csv_filename):
        return []

    submissions = []
    with open(csv_filename, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        submissions = [datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S").date() for row in reader]

    return sorted(list(set(submissions)), reverse=True)