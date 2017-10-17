import csv

def addEmptyColumns(header, num):
    for i in range(num):
        header.append("")
    return header

with open("./output/table.csv", newline='') as file1:
    r = csv.reader(file1)
    data = [line for line in r]

with open("./output/final-table.csv", 'w', newline='') as file2:
    w = csv.writer(file2)
    header = ["PERILS6",
              "PERILS12",
              "PERILS11"]
    header = addEmptyColumns(header, 4)
    header.append("PERILS3")
    header = addEmptyColumns(header, 4)
    header.append("PERILS16")
    header = addEmptyColumns(header, 4)
    header.append("PERILS7")
    header = addEmptyColumns(header, 4)
    header.append("PERILS2")
    w.writerow(header)
    w.writerows(data)