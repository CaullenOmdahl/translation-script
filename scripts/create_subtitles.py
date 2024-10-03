# scripts/create_subtitles.py

import os
import sys
import json
import srt
import logging
from datetime import timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CreateSubtitles')

def create_srt_files(translation_cache_path, transcript_cache_path, output_dir):
    try:
        # Load transcript cache
        with open(transcript_cache_path, 'r', encoding='utf-8') as f:
            transcript_cache = json.load(f)
        
        # Load translation cache
        with open(translation_cache_path, 'r', encoding='utf-8') as f:
            translation_cache = json.load(f)
        
        # Extract target language from translation_cache_path
        target_lang = os.path.splitext(os.path.basename(translation_cache_path))[0].split('_')[-1]
        
        subtitles = []
        for segment in transcript_cache['segments']:
            segment_id = segment['id']
            translated_text = translation_cache.get(str(segment_id), {}).get(target_lang, "[Translation Not Available]")
            subtitle = srt.Subtitle(
                index=segment_id + 1,
                start=timedelta(seconds=segment['start']),
                end=timedelta(seconds=segment['end']),
                content=translated_text
            )
            subtitles.append(subtitle)
        
        # Write SRT file with appropriate naming convention
        os.makedirs(output_dir, exist_ok=True)
        srt_content = srt.compose(subtitles)
        video_filename = os.path.splitext(os.path.basename(transcript_cache_path))[0].replace('transcript_cache_', '')
        srt_filename = f"subtitles_{target_lang}.srt"
        output_path = os.path.join(output_dir, srt_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        logger.info(f"SRT file for '{target_lang}' written to '{output_path}'.")
    
    except Exception as e:
        logger.error(f"Error during subtitle creation: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Usage: python create_subtitles.py <translation_cache_path> <transcript_cache_path> <output_dir>")
        print("Example: python create_subtitles.py cache/translation_cache_en.json cache/transcript_cache.json subtitles")
        sys.exit(1)
    
    translation_cache_path = sys.argv[1]
    transcript_cache_path = sys.argv[2]
    output_dir = sys.argv[3]
    
    create_srt_files(translation_cache_path, transcript_cache_path, output_dir)

if __name__ == "__main__":
    main()
