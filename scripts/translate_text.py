# translate_text.py

import os
import sys
import logging
import json
import traceback
import srt
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from transformers import MarianTokenizer
from optimum.onnxruntime import ORTModelForSeq2SeqLM

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TranslateText')

def translate_segment(segment, models, target_languages, translation_cache, use_profanity=False):
    try:
        index = segment['id'] + 1
        start = timedelta(seconds=segment['start'])
        end = timedelta(seconds=segment['end'])
        original_text = segment['text'].strip()
        segment_id = segment['id']

        subtitles = {}
        for lang in target_languages:
            if lang in models:
                model, tokenizer = models[lang]
                # Check cache
                if str(segment_id) in translation_cache and lang in translation_cache[str(segment_id)]:
                    translated_text = translation_cache[str(segment_id)][lang]
                else:
                    # Perform translation
                    try:
                        inputs = tokenizer(original_text, return_tensors="pt")
                        outputs = model.generate(**inputs, max_length=512, use_cache=False)
                        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                        # Update cache
                        if str(segment_id) not in translation_cache:
                            translation_cache[str(segment_id)] = {}
                        translation_cache[str(segment_id)][lang] = translated_text
                    except Exception as e:
                        logger.error(f"Error translating segment {segment_id} to '{lang}': {e}")
                        translated_text = "[Translation Error]"
            else:
                translated_text = "[Translation Not Available]"
                logger.error(f"Translation model for '{lang}' is not loaded.")
            
            subtitle = srt.Subtitle(
                index=index,
                start=start,
                end=end,
                content=translated_text
            )
            subtitles[lang] = subtitle
        return subtitles
    except Exception as e:
        logger.error(f"Error in translate_segment: {e}")
        logger.debug(traceback.format_exc())
        return {}

def translate_text(transcript_segments, models, target_languages, translation_cache_path, use_profanity=False):
    try:
        # Load existing translation cache
        if os.path.exists(translation_cache_path):
            with open(translation_cache_path, 'r', encoding='utf-8') as f:
                translation_cache = json.load(f)
            logger.info("Translation cache loaded.")
        else:
            translation_cache = {}

        translated_subtitles = {lang: [] for lang in target_languages}

        logger.info("Translating segments...")
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    translate_segment, 
                    segment, 
                    models, 
                    target_languages, 
                    translation_cache, 
                    use_profanity
                ): segment for segment in transcript_segments
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc="Translating", unit="segment"):
                subtitles = future.result()
                for lang, subtitle in subtitles.items():
                    translated_subtitles[lang].append(subtitle)

        # Save updated translation cache
        with open(translation_cache_path, 'w', encoding='utf-8') as f:
            json.dump(translation_cache, f, ensure_ascii=False, indent=4)
        logger.info(f"Translation cache updated at '{translation_cache_path}'.")

        # Write SRT files
        for lang, subs in translated_subtitles.items():
            srt_content = srt.compose(subs)
            output_path = os.path.join("subtitles", f"subtitles_{lang}.srt")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            logger.info(f"Subtitles for '{lang}' written to '{output_path}'.")

    except Exception as e:
        logger.error(f"Error during translation: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python translate_text.py <transcript_cache_path> <model_dir> <target_langs_comma_separated> <translation_cache_path> <use_profanity (y/n)>")
        print("Example: python translate_text.py cache/transcript_cache.json models/opus-mt-vi-en en cache/translation_cache.json n")
        sys.exit(1)
    
    transcript_cache_path = sys.argv[1]
    model_dir = sys.argv[2]
    target_langs = sys.argv[3].split(',')
    translation_cache_path = sys.argv[4]
    profanity_input = sys.argv[5].lower()
    use_profanity = profanity_input in ['y', 'yes']

    # Load models
    from load_model import load_translation_model

    model, tokenizer = load_translation_model(model_dir)
    models = {lang: (model, tokenizer) for lang in target_langs}

    # Load transcript segments
    if not os.path.exists(transcript_cache_path):
        print(f"Transcript cache '{transcript_cache_path}' not found.")
        sys.exit(1)
    
    with open(transcript_cache_path, 'r', encoding='utf-8') as f:
        transcript_segments = json.load(f)
    
    translate_text(transcript_segments, models, target_langs, translation_cache_path, use_profanity)
    print("Translation completed successfully.")
