import csv


class CSV:
    csvURL = None
    columnDict = None
    rowDict = None

    def __init__(self, csvURL, columnDict, rowDict):
        self.csvURL = csvURL
        self.columnDict = columnDict
        self.rowDict = rowDict

    def outputCSVFile(self):
        with open(self.csvURL, 'w', newline='') as csvFile:
            writer = self.__initHeaders(csvFile)
            writer.writerow(self.rowDict)
        csvFile.close()

    def __initHeaders(self, csvFile):
        writer = csv.DictWriter(csvFile, fieldnames=self.columnDict)
        writer.writeheader()
        return writer
