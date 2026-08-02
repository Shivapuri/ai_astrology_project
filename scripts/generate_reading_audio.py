import os
import re
import ssl
import subprocess
import torch
import torchaudio as ta
import nltk
from nltk.tokenize import sent_tokenize

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK tokenizers if needed
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

from chatterbox.tts import ChatterboxTTS

# Paths
ASTRA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(ASTRA_DIR, "western", "native_1983_full_reading_report.md")
TTS_VOICE_PATH = "/Users/hajnaljanos/PycharmProjects/Opensource_tts/voices/Artlist_Esteem.wav"
OUTPUT_DIR = os.path.join(ASTRA_DIR, "western", "audio_temp_chunks")
FINAL_WAV_PATH = os.path.join(ASTRA_DIR, "western", "native_1983_reading_audio.wav")
FINAL_MP3_PATH = os.path.join(ASTRA_DIR, "western", "native_1983_reading_audio.mp3")

def clean_markdown_for_speech(text):
    """Clean markdown styling, degree symbols, and formatting for fluid vocal speech."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('#') or line == '---' or not line:
            # Add pause between sections
            cleaned_lines.append("")
        else:
            cleaned_lines.append(line)
    
    text = " ".join(cleaned_lines)
    
    # Replace degrees and astrological notation
    # e.g., 0°42' -> 0 degrees and 42 minutes of
    text = re.sub(r'(\d+)°(\d+)\'?', r'\1 degrees and \2 minutes of', text)
    
    # Strip out markdown bold, italics, bullets
    text = re.sub(r'[\*\#\_\|]', ' ', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # remove markdown links, preserve text
    
    # Replace common abbreviations for clearer pronunciation
    text = text.replace("WSH", "Whole Sign Houses").replace("e.g.,", "for example,")
    
    # Remove excess whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    print("--- Astrological Reading Audio Generator ---")
    if not os.path.exists(REPORT_PATH):
        print(f"Error: Report file not found at {REPORT_PATH}")
        return

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print("Cleaning text for speech synthesis...")
    speech_text = clean_markdown_for_speech(raw_text)

    # Detect device (MPS for Apple Silicon)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Initializing Chatterbox TTS engine on device: {device}...")
    
    map_location = torch.device(device)
    torch_load_original = torch.load
    def patched_torch_load(*args, **kwargs):
        if 'map_location' not in kwargs:
            kwargs['map_location'] = map_location
        return torch_load_original(*args, **kwargs)
    torch.load = patched_torch_load

    model = ChatterboxTTS.from_pretrained(device=device)

    # Group into readable sentence chunks (max ~450 characters each)
    print("Tokenizing script into vocal narrative chunks...")
    sentences = sent_tokenize(speech_text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= 450:
            current_chunk += f"{sentence} "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = f"{sentence} "
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    print(f"Divided narrative into {len(chunks)} continuous audio segments.")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_wavs = []
    for idx, chunk in enumerate(chunks, start=1):
        print(f"Synthesizing Segment [{idx}/{len(chunks)}] ({len(chunk)} chars)...")
        wav = model.generate(
            chunk,
            audio_prompt_path=TTS_VOICE_PATH,
            exaggeration=1.5,
            cfg_weight=0.45
        )
        chunk_file = os.path.join(OUTPUT_DIR, f"chunk_{idx:03d}.wav")
        ta.save(chunk_file, wav, model.sr)
        all_wavs.append(wav)

    print("\nConcatenating audio segments into final master recording...")
    if all_wavs:
        concatenated_wav = torch.cat(all_wavs, dim=-1)
        ta.save(FINAL_WAV_PATH, concatenated_wav, model.sr)
        print(f"[*] Successfully created Master Audio Recording: {FINAL_WAV_PATH}")

        # Attempt mp3 conversion via ffmpeg
        try:
            cmd = ['ffmpeg', '-i', FINAL_WAV_PATH, '-b:a', '192k', '-y', FINAL_MP3_PATH]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"[*] Successfully converted to MP3 format: {FINAL_MP3_PATH}")
        except Exception as e:
            print(f"Notice: MP3 conversion via ffmpeg skipped or unsuccessful ({e}). WAV file remains ready.")

        # Cleanup temporary audio chunks
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
        os.rmdir(OUTPUT_DIR)
        print("Cleaned up temporary vocal segments.")

    print("--- Audio Generation Complete! ---")

if __name__ == "__main__":
    main()
