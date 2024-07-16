import socket
import os
import numpy as np
import librosa
import sounddevice as sd
import soundfile as sf
from scipy import signal
from multiprocessing import Process, Value
import ctypes

class AudioClassifierApp:
    def __init__(self):
        self.default_folder = r"D:\Audio_classification_final\uploads"
        os.makedirs(self.default_folder, exist_ok=True)
        print("Folder exists or created")
        
        self.master_audio_path = os.path.join(self.default_folder, "master_audio.wav")
        self.test_audio_path = os.path.join(self.default_folder, "test_audio.wav")
        print(f"Master audio path: {self.master_audio_path}")
        print(f"Test audio path: {self.test_audio_path}")
        
        self.sample_rate = 44100
        self.master_duration = 2
        self.test_duration = 0.7
        self.window_size = 2048
        self.min_freq = 100
        self.max_freq = 5000
        self.continuous_test_recording = Value(ctypes.c_bool, False)
        self.recording_process = None

    def record_audio(self, filename, duration):
        try:
            print(f"Recording audio for {duration} seconds and saving to {filename}")
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='float32')
            print("Recording in progress...")
            sd.wait()
            print("Recording finished")

            print("Applying band-pass filter")
            b, a = signal.butter(4, [self.min_freq/(self.sample_rate/2), self.max_freq/(self.sample_rate/2)], 'band')
            filtered_recording = signal.filtfilt(b, a, recording[:, 0])
            print("Band-pass filter applied")
            
            print(f"Saving the filtered recording to {filename}")
            sf.write(filename, filtered_recording, self.sample_rate)
            print("Recording saved successfully")
            
            return filename
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    def record_master_audio(self):
        try:
            print("Starting to record master audio")
            filename = self.master_audio_path
            recorded_file = self.record_audio(filename, self.master_duration)
            
            if recorded_file:
                print(f"Recorded master audio: {recorded_file}")
                self.continuous_test_recording.value = True
                self.recording_process = Process(target=self.listen_for_test_audio)
                self.recording_process.start()
        except Exception as e:
            print(f"Error recording master audio: {e}")

    def stop_all_processes(self):
        self.continuous_test_recording.value = False
        if self.recording_process:
            self.recording_process.join()
        print("Stopped all processes.")
    
    def find_peak_frequency(self, audio_segment):
        try:
            n = len(audio_segment)
            yf = np.fft.fft(audio_segment)
            xf = np.fft.fftfreq(n, 1 / self.sample_rate)[:n // 2]
            yf_abs = np.abs(yf[:n // 2])
            
            valid_indices = np.where((xf >= self.min_freq) & (xf <= self.max_freq))
            dominant_freq_index = valid_indices[0][np.argmax(yf_abs[valid_indices])]
            dominant_freq = xf[dominant_freq_index]
            
            return dominant_freq
        except Exception as e:
            print(f"Error processing audio segment: {e}")
            return None

    def listen_for_test_audio(self):
        try:
            while self.continuous_test_recording.value:
                filename = self.test_audio_path
                self.record_audio(filename, self.test_duration)
                self.compare_audio()
        except Exception as e:
            print(f"Error recording or comparing test audio: {e}")

    def compare_audio(self):
        if not self.master_audio_path or not self.continuous_test_recording.value:
            return
        
        try:
            print("Comparing test audio with master audio")
            master_audio, _ = librosa.load(self.master_audio_path, sr=self.sample_rate)
            master_freq = self.find_peak_frequency(master_audio)
            
            if master_freq is None:
                print("Master frequency not found")
                return
            
            proceed_tolerance = (15 / 100) * master_freq
            match_tolerance = (12 / 100) * master_freq
            valid_freq_range = (master_freq - proceed_tolerance, master_freq + proceed_tolerance)
            
            test_audio_path = self.test_audio_path
            test_audio, _ = librosa.load(test_audio_path, sr=self.sample_rate)
            test_freq = self.find_peak_frequency(test_audio)

            print(f"Test frequency: {test_freq}")

            if test_freq is None:
                return
            
            if valid_freq_range[0] <= test_freq <= valid_freq_range[1]:
                freq_diff = np.abs(master_freq - test_freq)
                print("In frequency difference check")
                
                if freq_diff <= match_tolerance:
                    result_message = f"Matched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
                    print(f"Matched: {result_message}")
                    self.send_message_to_server(result_message)
                else:
                    result_message = f"Mismatched: Master Frequency = {master_freq:.2f} Hz, Test Frequency = {test_freq:.2f} Hz"
                    print(f"Mismatched: {result_message}")
                    self.send_message_to_server(result_message)
            else:
                result_message = f"Ignored: Master Frequency = {master_freq:.2f} Hz  Test Frequency = {test_freq:.2f} Hz (Outside ±10% range of Master Frequency)"
                print(f"Ignored: {result_message}")
                self.send_message_to_server(result_message)
        
        except Exception as e:
            print(f"Error comparing audio files: {e}")

    def send_message_to_server(self, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', 5004))
            client_socket.send(message.encode('utf-8'))
            client_socket.close()
        except Exception as e:
            print(f"Error sending message to server: {e}")

    def start_comparison(self):
        try:
            if self.master_audio_path:
                print(f"Starting comparison with last recorded master audio: {self.master_audio_path}")
                self.continuous_test_recording.value = True
                self.recording_process = Process(target=self.listen_for_test_audio)
                self.recording_process.start()
            else:
                print("No master audio recorded yet.")
        except Exception as e:
            print(f"Error starting comparison: {e}")

def start_server():
    app = AudioClassifierApp()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 5003))
    server_socket.listen(1)
    print("Server is listening...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address} has been established.")

        message = client_socket.recv(1024).decode('utf-8')
        print(f"Received message: {message}")
        
        if message == 'master':
            app.record_master_audio()
        elif message == 'compare':
            print("in compare from start server")
            app.start_comparison()
        elif message == 'stop all':
            app.stop_all_processes()

        response = f"Echo: {message}"
        client_socket.send(response.encode('utf-8'))
        client_socket.close()

if __name__ == "__main__":
    start_server()
