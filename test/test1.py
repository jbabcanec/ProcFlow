import csv
import random

def generate_csv(filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Value"])

        for i in range(10):
            writer.writerow([i, random.randint(1, 100)])

if __name__ == "__main__":
    generate_csv("sample.csv")
