import math
import time, audioop
import pyaudio
import pyaudio
import alsa_error_handler


# 34 dBA (decibels adjusted) if the underlying level of noise is no more than 24 dBA
# 10 dBA above the underlying level of noise if this is more than 24 dBA
# underlying level = 40 so trigger should be 50
TRIGGER_DECIBEL = 60

# Initialisation constants for PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1


def audio_init():
	"""Start py audio"""
	with alsa_error_handler.noalsaerr():
		p_audio = pyaudio.PyAudio()
	stream = p_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
	return p_audio, stream 


def audio_terminate(p_audio, stream):
	"""clearing the resources"""
	stream.stop_stream()
	stream.close()
	p_audio.terminate()


def audio_test_too_noisy(stream):
	"""Test if audio stream is above threshold return True or None"""
	decibel = 0
	# Read data from device for 1 sec
	for i in range(0,int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		# a measure of the power in an audio signal:
		rms = audioop.rms(data, 2)
		decibel = 20 * math.log10(rms)
		# print("volume  = " + str(decibel))
		if decibel > TRIGGER_DECIBEL:
			return decibel
		time.sleep(0.0001)


def noise_trigger():
	"""Listen to the microphone and trigger if there is noise"""
	p_audio, stream = audio_init()
	test = audio_test_too_noisy(stream)
	if test is None:
		test = False
	else: 
		print("Noise is too loud")
	audio_terminate(p_audio, stream)
	return test


def audio_stop(p_audio, stream, audio_frames):
	"""Termination of the audio stream"""
	stream.stop_stream()
	stream.close()
	p_audio.terminate()





