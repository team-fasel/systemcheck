import datetime

def getIntervalDate(interval:str, interval_type, basetime:datetime, operation:str):
    """
    Calculate the Lower Date/Time Limit
    ===================================

    :param interval: A numeric value specifying the interval lenght
    :param interval_type: Potential Values:
        - W: Weeks
        - D: Days
        - H: Hours
        - M: Minutes
        - S: Seconds

    :param basetime: datetime object on which the lower limit will be calculated.
    :param operator: '+' for adding or '-' for substracting from base time

    :return: datetime object of the lower limit or False
    """
    if interval_type.upper() == 'D':
        if operation=='+':
            return basetime + datetime.timedelta(days=+int(interval))
        else:
            return basetime + datetime.timedelta(days=-int(interval))
    elif interval_type.upper() == 'H':
        if operation=='+':
            return basetime + datetime.timedelta(hours=+int(interval))
        else:
            return basetime + datetime.timedelta(hours=-int(interval))
    elif interval_type.upper() == 'M':
        if operation=='+':
            return basetime + datetime.timedelta(minutes=+int(interval))
        else:
            return basetime + datetime.timedelta(minutes=-int(interval))
    elif interval_type.upper() == 'S':
        if operation=='+':
            return basetime + datetime.timedelta(seconds=+int(interval))
        else:
            return basetime + datetime.timedelta(seconds=-int(interval))
    elif interval_type.upper() == 'W':
        if operation=='+':
            return basetime + datetime.timedelta(weeks=+int(interval))
        else:
            return basetime + datetime.timedelta(weeks=-int(interval))
    else:
        return False