import datetime

MONTH_DAYS = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 81,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}

def month_days(month, year):
    if month != 2: return MONTH_DAYS[month]
    if year % 4 == 0: return 29
    return 28

def today():
    today = str(datetime.date.today()).split("-")
    return int(today[0]), int(today[1]), int(today[2])

def stringify(year, month, day):
    return f"{str(year).zfill(4)}-{str(month).zfill(2)}-{str(day).zfill(2)}"

def get_dates(year: int, month: int, day: int, dates_back: int, dates_ahead: int):
    dates = []
    date_back = (year, month, day)
    for y in range(dates_back):
        date_back = yesterday(*date_back)
        dates.append(stringify(*date_back))
    dates.reverse()
    dates.append(stringify(year, month, day))
    date_ahead = (year, month, day)
    for t in range(dates_ahead):
        date_ahead = tomorrow(*date_ahead)
        dates.append(stringify(*date_ahead))
    return dates

def yesterday(year: int, month: int, day: int):
    if day != 1: return year, month, day - 1
    if month != 1: return year, month - 1, month_days(month - 1, year)
    return year - 1, 12, 31

def tomorrow(year: int, month: int, day: int):
    if day != month_days(month, year): return year, month, day + 1
    if month != 12: return year, month + 1, 1
    return year + 1, 1, 1

def get_now(seconds_delta: int = 0):
    return [part for part in str(datetime.datetime.now() + datetime.timedelta(0, seconds_delta)).replace("-", " ").replace(":", " ").replace(".", " ").split(" ")[:-1]]

def get_now_as_string(seconds_delta: int = 0):
    arr = get_now(seconds_delta)
    return "-".join(arr[:3]) + "_" + "-".join(arr[3:])

def get_now_as_readable(seconds_delta: int = 0):
    arr = get_now(seconds_delta)
    return "/".join(arr[:3]) + " " + ":".join(arr[3:])

def is_after(dt_list_before, dt_list_after):
    for i in range(6):
        if int(dt_list_before[i]) < int(dt_list_after[i]): return True
        elif int(dt_list_before[i]) > int(dt_list_after[i]): return False
    return False