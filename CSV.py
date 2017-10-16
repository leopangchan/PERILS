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
            writer = self.__initHeaders(csvFile)
            writer.writerow(self.rowsDict)
        csvFile.close()

    def __initHeaders(self, csvFile):
        writer = csv.DictWriter(csvFile, fieldnames=self.columnDict)
        writer.writeheader()
        return writer
    
    '''
      It calculates the sum of all values in a column for colName
      @param colName - the name of a column where the sum is calculated.
    '''
    def getColumnSum(colName):
      r = [item[colName] for item in self.rowsDict]
      print ("list of columnSum = ", r)
      return sum(r)

    '''
      It loops a list of colName to the sum of the sum of ColumnSum of each
      column. 
      @param colNames - a list of colName
    '''
    def getTotalColumnsSum(colNames):
      allColumnsSum = 0
      for colName in colNames:
         allColumnsSum += getColumnSum(colName)
      return allColumnsSum

    '''
      Calculate the ratio of colName's sum / allColumnsSum
      @param colName - the column for which a ratio is calculated
      @param colNames - the set of columns that colName belongs to
    '''
    def getRatioForOneColumn(colName, colNames):
      return getColumnSum(colName) / getTotalColumnsSum(colNames)
