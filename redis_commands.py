import csv
from csv_downloader import get_todays_csv_file

csv_file = get_todays_csv_file()
with open(csv_file, 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    next(csvReader)
    for row in csvReader:
        print('HMSET \"{}\" code \"{}\" name \"{}\" open \"{}\" high \"{}\" low \"{}\" close \"{}\"\r'.format(row[1].strip() , row[0], row[1].strip(), row[4], row[5], row[6], row[7]))
        print('ZADD open {} \"{}\"\r'.format(float(row[4]), row[1].strip()))
