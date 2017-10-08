STATE_STR = "status"
OPEN_STR = "Open"
IN_PROGRESS_STR = "In Progress"
REOPENED_STR = "Reopened"
RESOLVED_STR = "Resolved"
CLOSED_STR = "Closed"
STATUSES = [OPEN_STR, IN_PROGRESS_STR, REOPENED_STR, RESOLVED_STR, CLOSED_STR]

def getAllPossibleTransitions():
    transitions = {}
    for indx, val in enumerate(STATUSES):
        for indx2, val2 in enumerate(STATUSES):
            if indx != indx2:
                transitions[val + "|" + val2] = [val, val2]
    return transitions