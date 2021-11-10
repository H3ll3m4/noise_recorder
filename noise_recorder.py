# module singleton to take only one video at a time
import math
import time, audioop
import pyaudio
from datetime import date, datetime
import cv2
import subprocess
import wave
import threading
import os
import update_diary
import send_email


# VIDEO_FILENAME = "temp_video.mp4"
# REENCODED_FILENAME = "temp_video2.mp4"
REENCODED_FILENAME = "temp_video2.avi"
VIDEO_FILENAME = "temp_video.avi"
AUDIO_FILENAME = "temp_audio.wav"


FOLDER = "~Videos/fou/"
# FOLDER = "home/hellema/fou/"
DURATION = 2 # 30
# 34 dBA (decibels adjusted) if the underlying level of noise is no more than 24 dBA
# 10 dBA above the underlying level of noise if this is more than 24 dBA
# underlying level = 40 so trigger should be 50
TRIGGER_DECIBEL = 50

# Initialisation for PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1

p_audio = pyaudio.PyAudio()
FPS = 6

#https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s03.html
class VideoThread(threading.Thread):
	def __init__(self, filename, name='VideoThread'):
		""" constructor, setting initial variables """
		# Capture video from webcam
		self.vid_capture = cv2.VideoCapture(0)
		# self.vid_cod = cv2.VideoWriter_fourcc(*"XVID")
		# self.vid_cod = cv2.VideoWriter_fourcc(*"mp4v")
		self.vid_cod = cv2.VideoWriter_fourcc(*"MJPG")
		self._stopevent = threading.Event()
		# self._stopevent.clear()
		self.frame_counts = 1
		self.filename = filename
		# self.output = cv2.VideoWriter(VIDEO_FILENAME, self.vid_cod, FPS, (640, 480))
		threading.Thread.__init__(self, name=name)


	def run(self):
		""" main control loop"""
		self.start_time = datetime.now()
		# time_elapsed = datetime.now().minute - self.start_time.minute
		time_elapsed = datetime.now().second - self.start_time.second
		if not self._stopevent.isSet():
		# while not self._stopevent.isSet():
		# while (time_elapsed < DURATION) and not self._stopevent.isSet():
			while (time_elapsed < DURATION):
				self.output = cv2.VideoWriter(VIDEO_FILENAME, self.vid_cod, FPS, (640, 480))
				ret, frame = self.vid_capture.read()
				if ret is True:
					cv2.putText(img=frame, text=make_video_txt(self.start_time), org=(50, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 255, 0),thickness=1)
					cv2.imshow(self.filename, frame)
					self.output.write(frame)
					self.frame_counts += 1
					# 0.16 because 6 FPS
					time.sleep(0.16)
					# time_elapsed = datetime.now().minute - self.start_time.minute
					time_elapsed = datetime.now().second - self.start_time.second
					if cv2.waitKey(1) & 0xFF == ord("x"):
						self._stopevent.set()
						break
			self.output.release()
		# cv2.destroyAllWindows()
		# else:
		# 	print("Stop Event is set so I'm running without doing anything")


	def join(self, timeout=None):
		"""Termination of the thread"""
		# if not self._stopevent.is_set():
		self.output.release()
		# close the already opened camera
		self.vid_capture.release()
		# close the window and de-allocate any associated memory usage
		cv2.destroyAllWindows()		
		self._stopevent.set()
		threading.Thread.join(self,timeout)
		# else:
		# 	print("Stop Event is set so I can't terminate")
		# 	pass



def audio_start():
	"""Initialisation of the audio channel"""
	stream = p_audio.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)
	return stream


def audio_recording(stream):
	"""Main loop to record the audio"""
	audio_frames = []
	stream.start_stream()
	start = datetime.now()
	time_elapsed = datetime.now().second - start.second
	while(time_elapsed < DURATION):
		time_elapsed = datetime.now().second - start.second
		data = stream.read(CHUNK) 
		audio_frames.append(data)
	return audio_frames


def audio_stop(stream, audio_frames):
	"""Termination of the audio stream"""
	stream.stop_stream()
	stream.close()
	# p_audio.terminate()
	waveFile = wave.open(AUDIO_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(p_audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(audio_frames))
	waveFile.close()


def aggregate_audio_video(video_thread, filename):
	"""Audio and Vide has to be aggreagetd into a file"""
	# cmd = "ffmpeg -i "+ VIDEO_FILENAME +" -i "+ AUDIO_FILENAME +" -c:v copy -c:a aac " + filename
	# subprocess.call(cmd, shell=True)

	frame_counts = video_thread.frame_counts
	elapsed_time = datetime.now() - video_thread.start_time
	recorded_fps = frame_counts / elapsed_time.total_seconds()
	# Makes sure the threads have finished
	while threading.active_count() > 1:
		time.sleep(1)

	#    Merging audio and video signal
	if abs(recorded_fps - FPS ) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
		print("Re-encoding")
		cmd = "ffmpeg -r " + str(recorded_fps) + " -i "+ VIDEO_FILENAME + " -pix_fmt yuv420p -r 6 "+ REENCODED_FILENAME
		subprocess.call(cmd, shell=True)
		print("Muxing")
		# cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
		cmd = "ffmpeg -ac 2 -channel_layout stereo -i "+ AUDIO_FILENAME +" -i "+ REENCODED_FILENAME+" -pix_fmt yuv420p " + filename
		# cmd = "ffmpeg -i "+ REENCODED_FILENAME+" -i "+ AUDIO_FILENAME +" -c:v copy -c:a aac " + filename
		subprocess.call(cmd, shell=True)
	else:
		print("Normal recording\nMuxing")
		# cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p " + filename + ".avi"
		cmd = "ffmpeg -i "+ VIDEO_FILENAME + " -i "+ AUDIO_FILENAME +" -c:v copy -c:a aac " + filename
		subprocess.call(cmd, shell=True)


def clean_temp_file():
	""""Remove temporary files"""
	local_path = os.getcwd()
	if os.path.exists(str(local_path) + "/"+AUDIO_FILENAME):
		os.remove(str(local_path) + "/"+AUDIO_FILENAME)
	if os.path.exists(str(local_path) + "/"+VIDEO_FILENAME):
		os.remove(str(local_path) + "/"+VIDEO_FILENAME)
	if os.path.exists(str(local_path) + "/"+REENCODED_FILENAME):
		os.remove(str(local_path) + "/"+REENCODED_FILENAME)


def terminate(stream):
	"""clearing the resources"""
	stream.stop_stream()
	stream.close()
	p_audio.terminate()


def buildfilename():
	"""Build filename by removing the digits at the end and the : separating the time"""
	time = datetime.now()
	filename = str(time).split(".")[0].replace(":","").replace("-","").replace(" ","_") + ".mp4"
	return filename


def make_video_txt(start_time):
	"""Retun a text to display in the video"""
	text = start_time.ctime()
	return text
	

def main():
	decibel = 0
	while True:
		try:
			# Now we read data from device for around one second
			# for i in range(0, 2):
			stream = audio_start()
			for i in range(0,int(RATE / CHUNK * RECORD_SECONDS)):
				data = stream.read(CHUNK)
				# a measure of the power in an audio signal:
				rms = audioop.rms(data, 2)
				decibel = 20 * math.log10(rms)
				print("volume  = " + str(decibel))
				if decibel > TRIGGER_DECIBEL:
					break
				time.sleep(0.0001)
			if decibel > TRIGGER_DECIBEL:
				filename = buildfilename()
				video_thread = VideoThread(filename)
				video_thread.start()
				audio_frames = audio_recording(stream)
				video_thread.join()
				# video_thread.join(timeout=float(DURATION+1)) # we use timeout so we're sure we close the window
				if video_thread.is_alive():
					print("Video thread is alive : Timeout")
				audio_stop(stream,audio_frames)
				aggregate_audio_video(video_thread,filename)
				print("Video is saved as " + filename)
				clean_temp_file()
				# update_diary.capture_in_diary(decibel,filename)
				# send_email.create_send_message(filename)
		except KeyboardInterrupt: # Ctrl-C 
			break
	terminate(stream)


if __name__ == "__main__" : 
	main()