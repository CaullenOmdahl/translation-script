# transcribe_audio.py

import os
import sys
import logging
import json
import traceback
from transformers import AutoProcessor
import whisper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TranscribeAudio')

def transcribe_video(video_path, source_lang, transcript_cache_path, no_cache=False):
    try:
        if not no_cache and os.path.exists(transcript_cache_path):
            logger.info(f"Loading transcription from cache: {transcript_cache_path}")
            with open(transcript_cache_path, 'r', encoding='utf-8') as f:
                transcript_segments = json.load(f)
            logger.info("Transcription loaded from cache.")
            return transcript_segments

        logger.info("Loading Whisper model...")
        model = whisper.load_model("base")  # Change model size as needed
        logger.info("Whisper model loaded.")

        logger.info("Starting transcription...")
        result = model.transcribe(video_path, language=source_lang, task='transcribe')
        transcript_segments = result['segments']

        # Ensure the cache directory exists
        os.makedirs(os.path.dirname(transcript_cache_path), exist_ok=True)
        # Save transcription to cache
        with open(transcript_cache_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_segments, f, ensure_ascii=False, indent=4)
        logger.info(f"Transcription completed and saved to '{transcript_cache_path}'.")

        return transcript_segments
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python transcribe_audio.py <video_path> <source_lang> <transcript_cache_path> [--no-cache]")
        print("Example: python transcribe_audio.py youtube_bfXjt1zTMwo_1920x1080_h264.mp4 vi cache/transcript_cache.json --no-cache")
        sys.exit(1)
    
    video_path = sys.argv[1]
    source_lang = sys.argv[2]
    transcript_cache_path = sys.argv[3]
    no_cache = '--no-cache' in sys.argv

    if not os.path.isfile(video_path):
        print(f"Video file '{video_path}' does not exist.")
        sys.exit(1)

    transcript_segments = transcribe_video(video_path, source_lang, transcript_cache_path, no_cache)
    print("Transcription completed successfully.")
