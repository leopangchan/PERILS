d1 = ['numOpenRequirements', 'numInProgressRequirements', 'ticket', 'numDevelopers', 'numDevelopedRequirementsBeforeThisInProgress', 'numDescOpen', 'numDescInProgress', 'numDescResolved', 'numDescReopened', 'numDescClosed', 'numCommitsOpen', 'numCommitsInProgress', 'numCommitsResolved', 'numCommitsReopened', 'numCommitsClosed', 'numOpenWhileThisOpen', 'numInProgressWhileThisOpen', 'numResolvedWhileThisOpen', 'numReopenedWhileThisOpen', 'numClosedWhileThisOpen', 'numOpenWhenInProgress', 'numInProgressWhenInProgress', 'numReopenedWhenInProgress', 'numResolvedWhenInProgress', 'numClosedWhenInProgress', 'Closed|Resolved', 'Open|In Progress', 'In Progress|Reopened', 'Closed|Reopened', 'Closed|Open', 'Reopened|In Progress', 'Reopened|Resolved', 'In Progress|Closed', 'Open|Closed', 'Resolved|Reopened', 'Open|Reopened', 'In Progress|Resolved', 'Open|Resolved', 'Reopened|Open', 'Resolved|In Progress', 'Resolved|Closed', 'Resolved|Open', 'In Progress|Open', 'Reopened|Closed', 'Closed|In Progress']

j1 = {'numInProgressRequirements': 38, 'numInProgressWhileThisOpen': 38, 'numClosedWhenInProgress': 'NA', 'numOpenWhileThisOpen': 197, 'Open|Closed': 0, 'numDescInProgress': 0, 'numReopenedWhileThisOpen': 14, 'Closed|Reopened': 0, 'ticket': 'TIKA-2332', 'numCommitsResolved': 0, 'numResolvedWhileThisOpen': 140, 'Reopened|Closed': 0, 'Open|In Progress': 0, 'Resolved|Reopened': 0, 'numDescClosed': 0, 'Resolved|Open': 0, 'Reopened|Open': 0, 'In Progress|Open': 0, 'numCommitsOpen': 1, 'numReopenedWhenInProgress': 'NA', 'Resolved|Closed': 0, 'numOpenWhenInProgress': 'NA', 'Resolved|In Progress': 0, 'Reopened|Resolved': 0, 'numDescReopened': 0, 'numCommitsReopened': 0, 'numDevelopers': 1, 'In Progress|Reopened': 0, 'Closed|Resolved': 0, 'numDescOpen': 0, 'Open|Reopened': 0, 'Open|Resolved': 1, 'Reopened|In Progress': 0, 'numCommitsClosed': 0, 'Closed|Open': 0, 'Closed|In Progress': 0, 'In Progress|Closed': 0, 'numDescResolved': 0, 'numDevelopedRequirementsBeforeThisInProgress': 'NA', 'numResolvedWhenInProgress': 'NA', 'In Progress|Resolved': 0, 'numCommitsInProgress': 0, 'numInProgressWhenInProgress': 'NA', 'numOpenRequirements': 197, 'numClosedWhileThisOpen': 63}

def findMissing():
   print ("d1's len = ", len(d1))
   print ("j1's len = ", len(j1))
   for jeach, val in j1.items():
      if jeach not in d1:
         print (jeach)

findMissing()
