import datetime


epoch_time = datetime.datetime.utcfromtimestamp(0)


def date_to_db(date: datetime.datetime = epoch_time):
    return date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def db_to_date(string: str):
    try:
        return datetime.datetime.strptime(string + '000', '%Y-%m-%d %H:%M:%S.%f')
    except Exception as ex:
        print(datetime.datetime.now())
        print(ex)
        print(string + '000')
        raise
