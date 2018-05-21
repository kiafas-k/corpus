import time
import datetime


def dateToTimestamp(date_string):
    date_elements = date_string.split('/')
    timestamp = datetime.datetime(int(date_elements[2]), int(
        date_elements[1]), int(date_elements[0]), 0, 0).timestamp()

    return int(timestamp)


print(dateToTimestamp('21/05/2018'))
