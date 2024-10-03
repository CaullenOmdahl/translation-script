# load_model.py

import os
import sys
import logging
import traceback
import GPUtil
from transformers import MarianTokenizer, AutoConfig
from optimum.onnxruntime import ORTModelForSeq2SeqLM
import onnxruntime as ort
import warnings
from torch.jit import TracerWarning  # Correct import for TracerWarning

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=TracerWarning)

# Setup logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs
logger = logging.getLogger('LoadModel')

def load_translation_model(model_dir):
    try:
        # Detect GPU
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_name = gpus[0].name
            logger.info(f"GPU detected: {gpu_name}. Attempting to use DirectML Execution Provider.")
            provider = "DmlExecutionProvider"
        else:
            logger.warning("No GPU detected. Falling back to CPU Execution Provider.")
            provider = "CPUExecutionProvider"

        # Load and modify the config
        config = AutoConfig.from_pretrained(model_dir)
        if hasattr(config, 'use_cache'):
            config.use_cache = False
            logger.debug(f"Set 'use_cache' to False in config for model '{model_dir}'.")

        # Log the current config
        logger.debug(f"Current config 'use_cache': {config.use_cache}")

        # Initialize session options
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        # Load the model with ORTModelForSeq2SeqLM
        logger.info("Loading the ONNX model using ORTModelForSeq2SeqLM...")
        model = ORTModelForSeq2SeqLM.from_pretrained(
            model_dir,
            config=config,
            session_options=session_options,
            provider=provider,
            use_cache=config.use_cache  # Explicitly pass use_cache
        )
        logger.info("Model loaded successfully.")

        # Load the tokenizer
        tokenizer = MarianTokenizer.from_pretrained(model_dir)
        logger.info("Tokenizer loaded successfully.")

        # Retrieve available execution providers directly from onnxruntime
        available_providers = ort.get_available_providers()
        logger.info(f"Available Execution Providers: {available_providers}")

        return model, tokenizer
    except Exception as e:
        logger.error(f"Failed to load ONNX model and tokenizer for '{model_dir}' with provider '{provider}': {e}")
        logger.debug(traceback.format_exc())
        if provider != "CPUExecutionProvider":
            logger.info("Attempting to fallback to CPU Execution Provider.")
            try:
                provider = "CPUExecutionProvider"
                model = ORTModelForSeq2SeqLM.from_pretrained(
                    model_dir,
                    config=config,
                    session_options=session_options,
                    provider=provider,
                    use_cache=False  # Ensure use_cache=False here as well
                )
                tokenizer = MarianTokenizer.from_pretrained(model_dir)
                logger.info(f"Successfully loaded model on CPU from '{model_dir}'.")
                return model, tokenizer
            except Exception as ex:
                logger.critical(f"Failed to load model on both GPU and CPU: {ex}")
                logger.debug(traceback.format_exc())
                sys.exit(1)
        else:
            logger.critical(f"Failed to load model on CPU: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_model.py <model_dir>")
        print("Example: python load_model.py models/opus-mt-vi-en")
        sys.exit(1)
    
    model_dir = sys.argv[1]
    if not os.path.isdir(model_dir):
        print(f"Model directory '{model_dir}' does not exist.")
        sys.exit(1)
    
    model, tokenizer = load_translation_model(model_dir)
    print("Model and tokenizer loaded successfully.")
