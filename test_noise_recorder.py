import pytest
import os 
from datetime import datetime
import update_diary
import noise_detector
import audio_recorder
import video_recorder
import multiplexing


def file_count():
	count_files = 0
	for files in os.walk(multiplexing.FOLDER):
		for files in multiplexing.FOLDER:
			count_files += 1
	return count_files


def test_get_date_time():
	date,time = update_diary.get_date_time("20211103_234752.mp4")
	assert date == "2021/11/03"
	assert time == "23:47:52"


def test_get_time_from_str():
	time = update_diary.get_time_from_str("20211103_234752")
	assert time == 23


def test_fill_info_if_sleeping():
	room, activity = update_diary.fill_info_if_sleeping(5)
	# assert room == "Bedroom 1"
	assert room == "Room Middle Floor Road Side"
	assert activity =="Sleeping"


def test_fill_info_if_working():
	room, activity = update_diary.fill_info_if_sleeping(15)
	# assert room == ""
	assert room == "Room Ground Floor Road Side"
	assert activity =="Working"


def test_buildfilename():
	filename = multiplexing.buildfilename()
	print(filename)
	assert len(filename) == 19 #it should look like that 20211107 112852.mp4 


def test_make_video_txt():
	time = datetime(2021, 11, 7, 14, 30, 46)
	txt = video_recorder.make_video_txt(time)
	assert txt == "Sun Nov  7 14:30:46 2021" 


def test_noise_trigger():
	silent_test = noise_detector.noise_trigger()
	assert silent_test is not True


def test_audio_loop():
	test = []
	for x in range(5): 
		test.append(noise_detector.noise_trigger())
		if test is True:
			print("Test " + str(x) + " : noise above threashold detected")
		else:
			print("Test " + str(x) + " : no noise detected")
	assert len(test) == 5



def test_audio_sequence():
	duration = 2
	audio_recorder.audio_sequence(duration)
	assert os.path.exists(audio_recorder.AUDIO_FILENAME)


def size_file(filepath):
	statinfo = os.stat(filepath)
	return statinfo.st_size


def test_audio_thread():
	duration = 2
	audio_recorder.thread_audio_only(duration)
	assert size_file(audio_recorder.AUDIO_FILENAME) > 340*1024, \
		"File is not bigger than 340kb unlikely to record more than 2sec audio"


def test_video_sequence():
	duration = 2
	video_recorder.thread_video_only(duration)
	assert size_file(video_recorder.VIDEO_FILENAME) > 35.4*1024 + 10 , \
		"File is not bigger than 340kb unlikely to record more than 2sec video"


def test_record_video_with_audio():
	duration = 2
	multiplexing.record_video_with_audio(duration)
	assert file_count() == 1


def test_record_video_with_audio_thread():
	duration = 2
	multiplexing.record_video_with_audio_threads(duration)
	assert file_count() == 1


