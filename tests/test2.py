import csv

def modify_csv(filename):
    data = []

    # Read the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # First row is the header
        data.append(headers)

        for row in reader:
            row[1] = str(int(row[1]) * 2)  # Double the value in the "Value" column
            data.append(row)

    # Write back to the same CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

if __name__ == "__main__":
    modify_csv("sample.csv")
