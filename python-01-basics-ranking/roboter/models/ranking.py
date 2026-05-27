import collections
import csv
import os


class RankingModel:
    def __init__(self, csv_file="ranking.csv"):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.csv_file = os.path.join(base_dir, csv_file)
        self.column = ["name", "count"]
        self.data = collections.defaultdict(int)
        self.load_data()

    def load_data(self):
        with open(self.csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.data[row["name"]] = int(row["count"])

        return self.data

    def save(self):
        with open(self.csv_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.column)
            writer.writeheader()
            for n, c in self.data.items():
                writer.writerow({"name": n, "count": c})

    def get_most_popular(self, not_list=None):
        if not_list is None:
            not_list = []

        if not self.data:
            return None

        sorted_data = sorted(self.data, key=self.data.get, reverse=True)
        for name in sorted_data:
            if name in not_list:
                continue
            return name

    def increment(self, name):
        self.data[name] += 1
        self.save()
