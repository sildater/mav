# mav
combined MIDI, audio, and video recording using a single script

requires: python, ffmpeg, mido
gets data from: settable audio and video devices via ffmpeg, settable MIDI device bia mido
stores data to: audio/video-> date_time.avi file / midi -> date_time.mid file

very simple, no guarantees. MIDI rec loop runs in python at 1kHz.
there's a slight (~1-2 sec) offset of the recordings due to ffmpeg startup time, but I didn't notice any other dynamic drift.

set your parameters, run the script, and stop it with ctrl+c.