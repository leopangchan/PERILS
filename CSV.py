import csv


class CSV:
    csvURL = None
    columnDict = None
    rowsDict = None

    def __init__(self, csvURL, columnDict, rowsDict):
        self.csvURL = csvURL
        self.columnDict = columnDict
        self.rowsDict = rowsDict

    def outputCSVFile(self):
        with open(self.csvURL, 'w', newline='') as csvFile:
          writer = csv.DictWriter(csvFile, fieldnames=self.columnDict)
          writer.writeheader()
          for row in self.rowsDict:
            writer.writerow(row)
            print ("one row = ", row)
        csvFile.close()

    def __initHeaders(self, csvFile):
        writer = csv.DictWriter(csvFile, fieldnames=self.columnDict)
        writer.writeheader()
        return writer
