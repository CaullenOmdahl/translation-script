# Scripts/run_all.py

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_script(script_path, args):
    """
    Executes a Python script with the given arguments using subprocess.
    """
    command = [sys.executable, script_path] + args
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"Error: {script_path} exited with return code {result.returncode}.")
        sys.exit(result.returncode)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run the entire video subtitle translation pipeline.")
    parser.add_argument('--video', type=str, required=True, help="Path to the input video file.")
    parser.add_argument('--source-lang', type=str, required=True, help="Source language code (e.g., vi, en, fr).")
    parser.add_argument('--target-langs', type=str, nargs='+', required=True, help="List of target language codes (e.g., en, fr).")
    parser.add_argument('--model-size', type=str, default='base', choices=['tiny', 'base', 'small', 'medium', 'large'], help="Whisper model size to use for transcription.")
    parser.add_argument('--output-dir', type=str, required=True, help="Directory to save the generated subtitles.")
    
    args = parser.parse_args()
    
    video_path = Path(args.video).resolve()
    source_lang = args.source_lang
    target_langs = args.target_langs
    model_size = args.model_size
    output_dir = Path(args.output_dir).resolve()
    
    scripts_dir = Path(__file__).resolve().parent
    models_dir = output_dir / "Models"
    cache_dir = output_dir / "Cache"
    subtitles_dir = output_dir / "Subtitles"
    
    # Validate video file existence
    if not video_path.is_file():
        print(f"Error: Video file '{video_path}' does not exist.")
        sys.exit(1)
    
    # Define paths
    video_name = video_path.stem
    video_output_dir = subtitles_dir / video_name
    video_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Move video to Output folder
    print(f"Moving video '{video_path.name}' to '{video_output_dir}'...")
    destination_video_path = video_output_dir / video_path.name
    try:
        if destination_video_path.exists():
            print(f"Video '{destination_video_path}' already exists in the Output directory.")
        else:
            video_path.rename(destination_video_path)
            print("Video moved successfully.")
    except Exception as e:
        print(f"Error moving video: {e}")
        sys.exit(1)
    
    # Define model information
    models_info = []
    for target_lang in target_langs:
        model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
        model_dir = models_dir / f'opus-mt-{source_lang}-{target_lang}'
        models_info.append({
            'target_lang': target_lang,
            'model_name': model_name,
            'model_dir': str(model_dir)
        })
    
    # Step 1: Setup Environment (Ensure it's already set up)
    # Assuming setup_environment.py has been run previously
    
    # Step 2: Download and Export Models for Each Target Language
    for model in models_info:
        target_lang = model['target_lang']
        model_name = model['model_name']
        model_dir = model['model_dir']
        print(f"\nStep 2: Downloading and exporting model '{model_name}'...")
        run_script(str(scripts_dir / 'download_export_model.py'), [model_name, model_dir])
    
    # Step 3: Load Models
    for model in models_info:
        target_lang = model['target_lang']
        model_dir = model['model_dir']
        print(f"\nStep 3: Loading model for target language '{target_lang}'...")
        run_script(str(scripts_dir / 'load_model.py'), [model_dir])
    
    # Step 4: Transcribe Audio
    transcript_cache_path = cache_dir / f'{video_name}_transcript.json'
    print("\nStep 4: Transcribing audio from the video...")
    run_script(str(scripts_dir / 'transcribe_audio.py'), [
        str(destination_video_path),
        source_lang,
        str(transcript_cache_path),
        '--model-size', model_size
    ])
    
    # Step 5: Translate Text for Each Target Language
    for model in models_info:
        target_lang = model['target_lang']
        model_dir = model['model_dir']
        translation_cache_path = cache_dir / f'{video_name}_translation_{target_lang}.json'
        print(f"\nStep 5: Translating text to '{target_lang}'...")
        run_script(str(scripts_dir / 'translate_text.py'), [
            str(transcript_cache_path),
            model_dir,
            target_lang,
            str(translation_cache_path),
            'n'  # 'n' for no profanity filtering; modify if needed
        ])
    
    # Step 6: Create Subtitles for Each Target Language
    for model in models_info:
        target_lang = model['target_lang']
        translation_cache_path = cache_dir / f'{video_name}_translation_{target_lang}.json'
        print(f"\nStep 6: Creating subtitles for '{target_lang}'...")
        run_script(str(scripts_dir / 'create_subtitles.py'), [
            str(translation_cache_path),
            str(transcript_cache_path),
            str(video_output_dir)
        ])
    
    print(f"\nAll steps completed successfully. Subtitles are available in the '{video_output_dir}' directory.")
    
    # Rename SRT files to match VLC's naming convention
    for target_lang in target_langs:
        original_srt = video_output_dir / f"{video_name}.srt"  # Assuming create_subtitles.py names it as video_name.srt
        renamed_srt = video_output_dir / f"{video_name}.{target_lang}.srt"
        if original_srt.exists():
            original_srt.rename(renamed_srt)
            print(f"Subtitle file renamed to '{renamed_srt.name}'.")
        else:
            print(f"Warning: Expected subtitle file '{original_srt}' not found.")

if __name__ == "__main__":
    main()
