from datetime import datetime
failed = True
while failed != False: # Get a valid date
    failed = False
    try:
        date_string = input("Enter a date: ")

        try:
            date = datetime.strptime(date_string, "%d/%m/%Y")
        except ValueError:
            date = datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            date = datetime.strptime(date_string, "%Y/%m/%d")

    except ValueError:
        print("Invalid date.")
        failed = True

total =  date.day + date.month + date.year

year = total//360
month = (total % 360) // 8
week = ((total % 360) % 8) // 5
day = (((total % 360) % 8) % 5) // 9

newdate = datetime(year,month,(day+week))

