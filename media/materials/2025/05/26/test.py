import sounddevice as sd
from scipy.io.wavfile import write

fs = 44100  # Sample rate (44.1 kHz)
seconds = 60  # Duration of recording

print("Recording...")
recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
sd.wait()  # Wait until recording is finished
write("voice.wav", fs, recording)
print("Done. Saved as voice.wav")



