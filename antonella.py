"""
Antonella — offline voice assistant for Windows.
Run:  python antonella.py
Stop: Ctrl+C
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.audio import MicStream, record_command, find_best_mic, find_best_speaker, drain_queue
from src.stt import Transcriber
from src.wake_word import WakeWordDetector
from src.tts import Speaker
from src.intent import parse
from src.router import route


def main():
    print("=" * 50)
    print("  Antonella — starting up")
    print("=" * 50)

    transcriber = Transcriber()
    mic_device = find_best_mic()
    speaker_device = find_best_speaker(mic_device)
    speaker = Speaker(output_device=speaker_device)
    detector = WakeWordDetector(transcriber=transcriber)

    print(f"\n[main] Mic: {mic_device} | Speaker: {speaker_device}")
    print("[main] Listening... say 'Antonella' (Ctrl+C to quit)\n")

    speaker.say("Antonella is ready.")

    with MicStream(device=mic_device) as mic:
        drain_queue(mic)

        while True:
            chunk = mic.read()
            fired, inline_cmd = detector.feed(chunk)

            if not fired:
                continue

            detector.reset()

            # If the command was spoken in the same breath as the wake word, use it
            if inline_cmd and len(inline_cmd.split()) >= 1:
                text = inline_cmd
                print(f"[main] Inline command: '{text}'")
            else:
                # Wake word only — ask for command
                speaker.say("Yes?")
                drain_queue(mic)

                print("[main] Listening for command...")
                audio = record_command(mic, listen_timeout=3.0)

                if audio is None:
                    print("[main] No speech — going back to sleep")
                    speaker.say("Okay.")
                    drain_queue(mic)
                    continue

                text = transcriber.transcribe(audio)
                print(f"[main] Heard: '{text}'")

                if not text or len(text.strip()) < 2:
                    speaker.say("I didn't catch that.")
                    drain_queue(mic)
                    continue

            intent = parse(text)
            print(f"[main] Intent: {intent.name} {intent.params}")

            try:
                response = route(intent)
            except Exception as e:
                print(f"[main] Error: {e}")
                traceback.print_exc()
                response = "Something went wrong."

            speaker.say(response)
            drain_queue(mic)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[main] Goodbye.")
        sys.exit(0)
