import math
import time, audioop
import pyaudio
from datetime import datetime
import wave
import threading
import pyaudio
import alsa_error_handler


AUDIO_FILENAME = "temp_audio.wav"

# Initialisation constants for PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1


class AudioThread(threading.Thread):
	def __init__(self, duration, name='AudioThread'):
		"""Start py audio"""
		with alsa_error_handler.noalsaerr():
			self.p_audio = pyaudio.PyAudio()
		self.stream = self.p_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
		self.audio_frames = []
		self._stopevent = threading.Event()
		# self._stopevent.clear()
		self.duration = duration
		threading.Thread.__init__(self, name=name)


	def run(self):
		"""Main loop to record the audio"""
		print("Start "+ self.getName())
		self.stream.start_stream()
		while not self._stopevent.isSet():
			data = self.stream.read(CHUNK) 
			self.audio_frames.append(data)
			if self._stopevent.isSet():
				break
		print("Stop "+ self.getName())


	def join(self, timeout=None):
		"""Termination of the audio stream"""
		self._stopevent.set()
		self.stream.stop_stream()
		self.stream.close()
		self.p_audio.terminate()
		print(self.getName() + " updating the wave file")
		waveFile = wave.open(AUDIO_FILENAME, 'wb')
		waveFile.setnchannels(CHANNELS)
		waveFile.setsampwidth(self.p_audio.get_sample_size(FORMAT))
		waveFile.setframerate(RATE)
		waveFile.writeframes(b''.join(self.audio_frames))
		waveFile.close()
		threading.Thread.join(self,timeout)



def audio_init():
	with alsa_error_handler.noalsaerr():
		p_audio = pyaudio.PyAudio()
	stream = p_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
	return p_audio, stream


def audio_recording(stream, duration):
	"""Main loop to record the audio"""
	audio_frames = []
	stream.start_stream()
	start = datetime.now()
	time_elapsed = datetime.now().second - start.second
	while(time_elapsed < duration):
		time_elapsed = datetime.now().second - start.second
		data = stream.read(CHUNK) 
		audio_frames.append(data)
	return audio_frames


def audio_stop(p_audio, stream, audio_frames):
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


def audio_sequence(duration):
	"""Initialise and record audio for a specific duration"""
	p_audio, stream  = audio_init()
	audio_frames = audio_recording(stream,duration)
	audio_stop(p_audio, stream, audio_frames)


def thread_audio_only(duration):
	"""Create a thread to record audio only in AUDIO_FILENAME for duration seconds"""
	audio_thread = AudioThread(duration)
	audio_thread.start()
	time.sleep(float(duration))
	audio_thread.join()