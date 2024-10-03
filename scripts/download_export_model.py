# scripts/download_export_model.py

import os
import sys
import logging
import traceback
from optimum.exporters.onnx import main_export

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DownloadExportModel')

def download_and_export(model_name, model_dir, task='text2text-generation'):
    try:
        logger.info(f"Downloading and exporting model '{model_name}' to '{model_dir}'...")
        main_export(
            model_name,    # model_name_or_path (positional argument)
            model_dir,     # output (positional argument)
            task=task,
            no_post_process=True,
            # You can add more arguments here if needed, such as opset, device, etc.
        )
        logger.info(f"Model '{model_name}' exported successfully to '{model_dir}'.")
    except Exception as e:
        logger.error(f"Error during model download and export: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: python download_export_model.py <model_name> <model_dir> [<task>]")
        print("Example: python download_export_model.py Helsinki-NLP/opus-mt-vi-en models/opus-mt-vi-en text2text-generation")
        sys.exit(1)
    
    model_name = sys.argv[1]
    model_dir = sys.argv[2]
    task = sys.argv[3] if len(sys.argv) > 3 else 'text2text-generation'
    
    download_and_export(model_name, model_dir, task)

if __name__ == "__main__":
    main()
