import json
import math
import queue
import struct
from collections import namedtuple
import numpy as np
import sounddevice as sd
from vosk import KaldiRecognizer, Model, SetLogLevel
power_now = 0
app_exit = False


class MicrophoneStream:
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk
        self.buff = queue.Queue()
        self.workspace = {"is_speaking": False, "count_on": 0, "count_off": 0, "voice_end": False, "str_current_power": ""}
        self.input_stream = None

    def open_stream(self):
        self.input_stream = sd.RawInputStream(samplerate=self.rate, blocksize=self.chunk, dtype="int16", channels=1, callback=self.callback)

    def callback(self, indata, frames, time, status):
        global power_now
        self.buff.put(bytes(indata))
        indata2 = struct.unpack(f"{len(indata) / 2:.0f}h", indata)
        rms = math.sqrt(np.square(indata2).mean())
        power_now = 20 * math.log10(rms) if rms > 0.0 else -math.inf

    def generator(self):
        while True:
            chunk = self.buff.get()
            if chunk is None: return
            data = [chunk]

            while True:
                try:
                    chunk = self.buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def app_exit_func():
    global app_exit
    app_exit = True

def voice_power(power = 60, wake_word = "起きたよ"):
    global app_exit
    SetLogLevel(-1)
    input_device_info = sd.query_devices(kind="input")
    sample_rate = int(input_device_info["default_samplerate"])
    mic_stream = MicrophoneStream(sample_rate, 8000)
    recognizer = KaldiRecognizer(Model("./module/model"), sample_rate)
    VoskStreamingASR = namedtuple("VoskStreamingASR", ["microphone_stream", "recognizer"])
    vosk_asr = VoskStreamingASR(mic_stream, recognizer)
    mic_stream = vosk_asr.microphone_stream

    mic_stream.open_stream()

    with mic_stream.input_stream:
        audio_generator = mic_stream.generator()
        for content in audio_generator:
            if vosk_asr.recognizer.AcceptWaveform(content):
                recog_result = json.loads(vosk_asr.recognizer.Result())
                recog_text = recog_result["text"].split()
                recog_text = "".join(recog_text)
                print(recog_text + ":" + str(power_now))
                if (recog_text == wake_word and power_now >= power): return False

            if app_exit == True:
                return False


if __name__ == "__main__":
    voice_power(10, "起きたよ")