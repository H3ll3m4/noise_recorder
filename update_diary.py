import os
import datetime
import sys


ROOMS = ["Room Middle Floor Road Side",
		"Room Middle Floor Garden Side",
		"Room Ground Floor Road Side",
		"Room Ground Floor Garden Side"]


def capture_in_diary(volume, filename):
	diary = open("diary.csv", "a")  # append mode
	# record = str(datetime.now()) + "," + ROOMS[1]+ "," + volume
	record = build_record(filename, str(volume))
	diary.write(record + "\n")
	diary.close()
	print("Incident at "+ str(volume) +" decibels captured in "+ filename)


def return_timestamp(filename):
	array = filename.split(".")
	return array[0]


def get_date_time(filename):
	timestamp = return_timestamp(filename).split("_")
	# print("Extracting date and time from ", timestamp)
	date = timestamp[0][:4]+"/"+timestamp[0][4:6] + "/"+timestamp[0][6:8]
	time = timestamp[1][:2]+":"+timestamp[1][2:4] + ":"+timestamp[1][4:6]
	return date, time


def get_time_from_str(dt_string):
	format = "%Y%m%d_%H%M%S"
	# print("Extracting hour from filename:" + dt_string)
	dt_object = datetime.datetime.strptime(dt_string, format)
	return dt_object.hour


def fill_info_if_sleeping(time):
	# if time.startswith("23") or time.startswith("00") or time.startwith("01") or time.startswith("02"):
	if time > 22 or time < 7 :
		# room = "Bedroom 1"
		room = ROOMS[0]
		doing = "Sleeping" 
	else:
		room = ROOMS[2]
		doing = "Working"
	return room, doing


def update_diary(path):
	diary = open("update_diary.csv", "w")  
	for filename in os.listdir(path):
		if filename.endswith(".mp4"):
			record = build_record(filename)
			diary.write(record + "\n")
	diary.close()


def build_record(filename, volume = "TBC"):
    date, time = get_date_time(filename)
    hour = get_time_from_str(return_timestamp(filename))
    room, doing = fill_info_if_sleeping(hour)
    record = date + "," + time + "," + "," + "," + "Shouting" + "," + room + "," + doing + "," + filename + "," + volume
    return record


def main():
	print('Number of arguments: ', len(sys.argv))
	print('The list of arguments: ', str(sys.argv))
	if len(sys.argv) < 2:
		# path = "~/Downloads/"
		# path = "../../Downloads"
		# path = "../../Downloads/"
		path = "."
	else : 
		path = sys.argv[1]
	print("Path to go through:", path)
	update_diary(path)
	

	
if __name__ == "__main__" : 
	main()