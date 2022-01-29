import subprocess
import threading
import os
import audio_video_recorder
import audio_recorder
import video_recorder
from datetime import datetime
import time


# REENCODED_FILENAME = "temp_video2.mp4"
REENCODED_FILENAME = "temp_video2.avi"

# FOLDER = "~Videos/fou/"
# FOLDER = "home/hellema/fou/"
FOLDER = "."


def aggregate_audio_video(video_thread, filepath):
	"""Audio and Video has to be aggregated into a file"""
	frame_counts = video_thread.frame_counts
	elapsed_time = datetime.now() - video_thread.start_time
	recorded_fps = frame_counts / elapsed_time.total_seconds()
	video_thread.join(timeout=float(video_thread.duration+1)) # we use timeout so we're sure we close the window
	if video_thread.is_alive():
		print("Video thread is alive : Timeout")

	# Makes sure the threads have finished
	while threading.active_count() > 1:
		time.sleep(1)

	#    Merging audio and video signal
	if abs(recorded_fps - video_recorder.FPS ) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
		print("Re-encoding")
		cmd = "ffmpeg -r " + str(recorded_fps) + " -i "+ video_recorder.VIDEO_FILENAME \
			+ " -pix_fmt yuv420p -r 6 "+ REENCODED_FILENAME
		subprocess.call(cmd, shell=True)
		print("Multiplexing")
		cmd = "ffmpeg -ac 2 -channel_layout stereo -i "+ audio_recorder.AUDIO_FILENAME \
			+" -i "+ REENCODED_FILENAME+" -pix_fmt yuv420p " + filepath
		# cmd = "ffmpeg -i "+ REENCODED_FILENAME+" -i "+ audio_recorder.AUDIO_FILENAME +" -c:v copy -c:a aac " + filepath
		subprocess.call(cmd, shell=True)
	else:
		print("Normal recording\nMultiplexing")
		cmd = "ffmpeg -ac 2 -channel_layout stereo -i "+ audio_recorder.AUDIO_FILENAME \
			+" -i "+ video_recorder.VIDEO_FILENAME + " -pix_fmt yuv420p " + filepath
		# cmd = "ffmpeg -i "+ video_recorder.VIDEO_FILENAME + " -i "+ audio_recorder.AUDIO_FILENAME +" -c:v copy -c:a aac " + filepath
		subprocess.call(cmd, shell=True)


def clean_temp_file():
	""""Remove temporary files"""
	local_path = os.getcwd()
	if os.path.exists(str(local_path) + "/"+audio_recorder.AUDIO_FILENAME):
		os.remove(str(local_path) + "/"+ audio_recorder.AUDIO_FILENAME)
	if os.path.exists(str(local_path) + "/"+ video_recorder.VIDEO_FILENAME):
		os.remove(str(local_path) + "/"+video_recorder.VIDEO_FILENAME)
	if os.path.exists(str(local_path) + "/"+REENCODED_FILENAME):
		os.remove(str(local_path) + "/"+REENCODED_FILENAME)


def buildfilename():
	"""Build filename by removing the digits at the end and the : separating the time"""
	time = datetime.now()
	filename = str(time).split(".")[0].replace(":","").replace("-","").replace(" ","_") + ".mp4"
	return filename


def buildfilepath():
	"""Build filepath of the file to store it in the right folder"""
	filename = buildfilename()
	filepath = os.path.join(FOLDER+ filename)
	return filepath


def recordaudiovideo(duration):
	"""Build the video using audio video recorder object"""
	# filepath = buildfilepath()
	filepath = buildfilename()
	audio_video_recorder.start_AVrecording(filepath)
	time.sleep(float(duration))
	audio_video_recorder.stop_AVrecording(filepath)


def record_video_with_audio(duration):
	"""Record a video with audio during the time duration"""
	# filepath = buildfilepath()
	filepath = buildfilename()
	print("Recording started")
	video_thread = video_recorder.VideoThread(duration)
	p_audio, stream = audio_recorder.audio_init()
	audio_frames = audio_recorder.audio_recording(stream, duration)
	video_thread.start()
	time.sleep(float(duration))
	video_thread.join(timeout=float(duration+1)) # we use timeout so we're sure we close the window
	if video_thread.is_alive():
		print("Video thread is alive : Timeout")
	audio_recorder.audio_stop(p_audio, stream, audio_frames)
	print("Recording finished")
	aggregate_audio_video(video_thread,filepath)
	print("Video is saved as " + filepath)
	clean_temp_file()
	# TODO: audio is not captured...


def record_video_with_audio_threads(duration):
	"""Record a video with audio during the time duration"""
	# filepath = buildfilepath() #TODO doesn't save in the right folder check user access
	filepath = buildfilename()
	video_thread = video_recorder.VideoThread(duration)
	audio_thread = audio_recorder.AudioThread(duration)
	audio_thread.start()
	video_thread.start()
	time.sleep(float(duration))
	print("Recording finished")
	audio_thread.join(timeout=float(duration+1))
	if audio_thread.is_alive():
		print("Audio thread is alive : Timeout")
	print("Audio recording has finished")
	aggregate_audio_video(video_thread,filepath)
	print("Video is saved as " + filepath)
	clean_temp_file()
