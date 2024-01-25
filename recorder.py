import subprocess
import os
from datetime import datetime
from mido import MidiFile, MidiTrack, MetaMessage
import mido
import time
import shlex

class Recorder(object):
    """
    stolen from 
    https://github.com/narcode/MIDI_recorder/blob/master/CK_rec/rec_classes.py
    and heavily modified
    """
    def __init__(self, port_name, debug=True):
        self.port_name = port_name
        self.port = mido.open_input(self.port_name)
        self.debug = debug
        self._mid = MidiFile()
        self._track = MidiTrack()
        self._mid.tracks.append(self._track)
        self.tempo = 120
        self._track.append(MetaMessage("set_tempo", tempo=500000, time=0))
        self._previous_time = 0
        self._arrival_time = 0
        self._delta_time = 0
        self._accumulated_delta_time = 0

        self._delta_midi_time = 0
        self._accumulated_delta_midi_time = 0

        self._init_time = 0
        self._total_time = 0
        self._total_midi_time = 0

    def setup(self):
        self._previous_time = time.perf_counter()
        self._init_time = self._previous_time
        print("midi: start recording")

    def __call__(self):
        for message in self.port.iter_pending():
            if message.type in [ "note_on", "note_off"]:
                self._arrival_time = time.perf_counter()
                self._delta_time = self._arrival_time - self._previous_time
                self._accumulated_delta_time += self._delta_time
                self._delta_midi_time = int(round(mido.second2tick(self._delta_time, self._mid.ticks_per_beat, mido.bpm2tempo(self.tempo))))
                self._accumulated_delta_midi_time += self._delta_midi_time
                self._previous_time = self._arrival_time
                
                self._total_time  = self._arrival_time - self._init_time
                self._total_midi_time = int(round(mido.second2tick(self._total_time, self._mid.ticks_per_beat, mido.bpm2tempo(self.tempo))))

                DIFF = abs(self._total_time - self._accumulated_delta_time)
                if DIFF > 0.01:
                    print("clock drift: ", DIFF)
                if self.debug:
                    print('deltatime: ', self._delta_time, 'msg: ', message)
                self._track.append(message.copy(time=self._delta_midi_time))

    def save(self, path):
        self._mid.save(path)

    def close(self):
        self.port.close()

def record_video(
        dt_string,
        out_path_video, 
        video_device,
        audio_device,
        number=0,
        video_framerate=30,
        ):
    
    """
    check available ffmpeg devices (on windows) with:
    ffmpeg -list_devices true -f dshow -i dummy

    check possible framerates and resolutions with:
    ffmpeg -f dshow -list_options true -i video="DEVICE_NAME" 

    """
    
    p = subprocess.Popen([
        'ffmpeg',
        '-f', 'dshow',
        '-framerate', str(video_framerate),
        '-video_size', '160x90',
        '-vcodec', 'mjpeg',
        '-i', 'video='+video_device+':audio='+audio_device+'',
        str(os.path.join(out_path_video,"video_{0}_{1}.avi".format(dt_string,number)))
    ])
    # stdout=subprocess.DEVNULL, 
    # stderr=subprocess.DEVNULL,
    # start_new_session=True
    # )

  



def record_midi(
        dt_string,
        out_path_midi=r"C:\Users\silva\Documents\repos\ZEDLES\test_and_develop",
        number=0,
        midi_device='seq 2'):
    recorder = Recorder(midi_device,debug=True)

    try:
        recorder.setup()
        while True:
            recorder()
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("midi: caught KeyboardInterrupt")
    finally:
        print('midi: save and close port') 
        recorder.close()
        recorder.save(os.path.join(out_path_midi,"midi_{0}_{1}.mid".format(dt_string,number)))


if __name__ == "__main__":

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    out_path_video="PATH/TO/AUDIOVIDEOOUTPUT"
    out_path_midi="PATH/TO/MIDIOUTPUT"
    # check names of available ffmpeg devices (on windows) with:
    # ffmpeg -list_devices true -f dshow -i dummy
    video_device="HD Pro Webcam C920"
    audio_device="Microphone (Realtek(R) Audio)"
    # check names of available mido devices with:
    # import mido; mido.get_input_names()
    midi_device="seq 2"

    try:
        print('main: starting recordings...')
        record_video(dt_string, out_path_video, video_framerate=30,
                video_device=video_device, audio_device=audio_device)
        record_midi(dt_string, out_path_midi, midi_device=midi_device)
        
    except KeyboardInterrupt:
        print(f'stop recordings...')
   




