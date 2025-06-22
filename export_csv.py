import csv
import json

csv.register_dialect("eur", delimiter=";")

RANDOM = "Bot-4000"


def compute_rank(clients):
    current_rank = 1
    nb_client_in_this_rank = 1
    current_points = clients[0]["points"]
    clients[0]["rank"] = current_rank

    for client in clients[1:]:
        if client["points"] == current_points:
            nb_client_in_this_rank += 1
            client["rank"] = current_rank
        else:
            current_rank += nb_client_in_this_rank
            current_points = client["points"]
            client["rank"] = current_rank
            nb_client_in_this_rank = 1


def load_data(log):
    with open(log, encoding="utf8") as file:
        content = json.load(file)

    compute_rank(content["clients"])

    students = []

    random_rank: int | None = None
    for client in content["clients"]:
        if client["name"] == RANDOM:
            random_rank = client["rank"]

    if random_rank is None:
        raise ValueError(f"{RANDOM} not found")

    for client in content["clients"]:
        if client["name"] == RANDOM:
            continue
        for matricule in client["matricules"]:
            grade = 2 if client["rank"] < random_rank else 0

            avg_bad_move = client["bad_moves"] / client["match_count"]
            grade += 0.5 if avg_bad_move < 3 else 0
            grade += 0.5 if avg_bad_move < 2 else 0
            grade += 0.5 if avg_bad_move < 1 else 0
            grade += 1 if client["bad_moves"] == 0 else 0

            grade += 2.5 if client["rank"] == 1 else 0
            grade += 2 if client["rank"] == 2 else 0
            grade += 1.5 if client["rank"] == 3 else 0
            grade += 1 if client["rank"] == 4 else 0
            grade += 0.5 if client["rank"] == 5 else 0

            students.append({"matricule": matricule, "grade": grade})

    return students


def main(title, log):
    students = load_data(log)

    with open(f"{title}.csv", "w", encoding="utf8", newline="") as csvfile:
        fieldnames = ["matricule", "grade"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect="eur")

        writer.writeheader()
        for student in students:
            row = {}
            row["matricule"] = student["matricule"]
            row["grade"] = str(student["grade"]).replace(".", ",")
            print(row)
            writer.writerow(row)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Exports grades in CSV")
    parser.add_argument("title", help="CSV file name")
    parser.add_argument("log", help="Competition Log JSON File")
    args = parser.parse_args()

    main(args.title, args.log)
