#!/Users/hajnaljanos/.local/bin/tts_venv/bin/python3
import os
import re
import sys
import argparse
import subprocess
import numpy as np
import soundfile as sf
import supertonic

# Paths
ASTRA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_PATH = os.path.join(ASTRA_DIR, "western", "native_1983_full_reading_report.md")
FINAL_WAV_PATH = os.path.join(ASTRA_DIR, "western", "native_1983_reading_audio.wav")
FINAL_MP3_PATH = os.path.join(ASTRA_DIR, "western", "native_1983_reading_audio.mp3")

def clean_markdown_for_speech(text):
    """Clean markdown styling, degree symbols, and formatting for fluid vocal speech."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('#') or line == '---' or not line:
            cleaned_lines.append("")
        else:
            cleaned_lines.append(line)
    
    text = " ".join(cleaned_lines)
    
    # Replace degrees and astrological notation (e.g., 0°42' -> 0 degrees and 42 minutes)
    text = re.sub(r'(\d+)°(\d+)\'?', r'\1 degrees and \2 minutes of', text)
    
    # Strip out markdown bold, italics, bullets, hashtags, backticks
    text = re.sub(r'[\*\#\`\_\|]', ' ', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # remove markdown links, preserve text
    text = re.sub(r'^[ \t]*[-+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[ \t]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Replace common abbreviations for clearer pronunciation
    text = text.replace("WSH", "Whole Sign Houses").replace("e.g.,", "for example,")
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    parser = argparse.ArgumentParser(description="Astrological Reading Audio Generator using Supertonic TTS")
    parser.add_argument("--report", default=REPORT_PATH, help="Path to input report markdown file")
    parser.add_argument("--voice", default="F1", help="Voice style (e.g., F1, F2, M1, M2)")
    parser.add_argument("--speed", type=float, default=1.1, help="Speech rate multiplier (default: 1.1)")
    parser.add_argument("--output-wav", default=FINAL_WAV_PATH, help="Path for generated WAV file")
    parser.add_argument("--output-mp3", default=FINAL_MP3_PATH, help="Path for generated MP3 file")
    args = parser.parse_args()

    print(f"--- Supertonic TTS Astrological Reading Audio Generator ---")
    print(f"Voice style: {args.voice} | Speed multiplier: {args.speed}")
    
    if not os.path.exists(args.report):
        print(f"Error: Report file not found at {args.report}")
        return

    with open(args.report, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print("Cleaning markdown text for fluid vocal synthesis...")
    speech_text = clean_markdown_for_speech(raw_text)

    print(f"Initializing Supertonic TTS engine...")
    tts = supertonic.TTS(auto_download=True)
    voice_style = tts.get_voice_style(args.voice)

    # Split into sentence chunks for smooth synthesis
    sentences = re.split(r'(?<=[.!?])\s+', speech_text)
    valid_sentences = []
    
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        try:
            is_valid, unsupported = tts.model.text_processor.validate_text(s)
            if not is_valid:
                for char in unsupported:
                    s = s.replace(char, '')
        except Exception:
            pass
        if s.strip():
            valid_sentences.append(s.strip())

    print(f"Synthesizing {len(valid_sentences)} narrative sentences...")
    
    audio_chunks = []
    total_duration = 0.0
    
    for idx, sentence in enumerate(valid_sentences, start=1):
        print(f"Synthesizing [{idx}/{len(valid_sentences)}] ({len(sentence)} chars): \"{sentence[:40]}...\"")
        try:
            wav, duration = tts.synthesize(
                text=sentence,
                lang="na",
                voice_style=voice_style,
                total_steps=8,
                speed=args.speed
            )
            # wav is shape (1, N), extract 1D samples
            samples = wav.squeeze()
            audio_chunks.append(samples)
            if isinstance(duration, (int, float)):
                total_duration += duration
            else:
                total_duration += float(np.sum(duration))
        except Exception as err:
            print(f"Warning: Failed to synthesize sentence {idx}: {err}")

    if not audio_chunks:
        print("Error: No audio segments were successfully generated.")
        return

    print("\nConcatenating audio segments into master recording...")
    final_audio = np.concatenate(audio_chunks)

    # Save WAV audio file
    sf.write(args.output_wav, final_audio, tts.sample_rate)
    print(f"[*] Successfully saved WAV audio recording: {args.output_wav}")
    print(f"[*] Total Audio Duration: {total_duration:.2f} seconds")

    # Convert to MP3 if ffmpeg is available
    try:
        cmd = ['ffmpeg', '-i', args.output_wav, '-b:a', '192k', '-y', args.output_mp3]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[*] Successfully converted to MP3 format: {args.output_mp3}")
    except Exception as e:
        print(f"Notice: MP3 conversion via ffmpeg skipped or unsuccessful ({e}). WAV file remains ready.")

    print("--- Audio Generation Complete! ---")

if __name__ == "__main__":
    main()
