# mic_test.py
import queue, json, sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = "vosk-model-small-pt-0.3"   # pasta do modelo
SAMPLE_RATE = 16_000                     # 16 kHz

model = Model(MODEL_PATH)
rec   = KaldiRecognizer(model, SAMPLE_RATE)

audio_q = queue.Queue()

def audio_callback(indata, frames, t, status):
    audio_q.put(bytes(indata))

with sd.RawInputStream(samplerate=SAMPLE_RATE,
                       blocksize=8000,            # 0,5 s de áudio
                       dtype='int16',
                       channels=1,
                       callback=audio_callback):
    print("=== Fale algo (Ctrl-C para sair) ===")
    try:
        while True:
            data = audio_q.get()
            if rec.AcceptWaveform(data):
                texto = json.loads(rec.Result())["text"]
                if texto:
                    print(f"\n🟢 {texto}")
            else:
                parcial = json.loads(rec.PartialResult())["partial"]
                # imprime transcrição parcial na mesma linha
                sys.stdout.write("\r⌛ " + parcial[:80])
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nEncerrado.")
