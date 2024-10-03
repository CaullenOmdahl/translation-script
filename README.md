```markdown
# Video Subtitle Translator

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![GitHub Issues](https://img.shields.io/github/issues/yourusername/video_subtitle_translator)
![GitHub Stars](https://img.shields.io/github/stars/yourusername/video_subtitle_translator?style=social)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Exporting Translation Models to ONNX](#exporting-translation-models-to-onnx)
- [Usage](#usage)
- [Caching Mechanism](#caching-mechanism)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Introduction

**Video Subtitle Translator** is a Python script that automates the process of transcribing audio from video files, translating the transcription into multiple target languages, and generating subtitle files in SRT format. It leverages powerful tools like OpenAI's Whisper for transcription, Hugging Face's MarianMT models for translation, and Optimum's `optimum-cli` for exporting models to the efficient ONNX format.

## Features

- **Audio Transcription:** Uses Whisper models to transcribe audio from video files.
- **Multi-Language Translation:** Translates transcriptions into multiple target languages using MarianMT models.
- **ONNX Optimization:** Exports translation models to ONNX format for improved performance using the `optimum-cli`.
- **Caching Mechanism:** Caches transcriptions and translations to speed up repeated runs.
- **Parallel Processing:** Translates multiple segments concurrently for faster processing.
- **Logging:** Comprehensive logging to monitor the script's operations and debug issues.
- **Profanity Filtering:** Detects and handles profanity in transcriptions to maintain subtitle quality.

## Prerequisites

- **Python Version:** Python 3.8 or higher.
- **Hardware:** 
  - **CPU:** Compatible with Whisper and ONNX Runtime.
  - **GPU (Optional):** For faster processing, especially during translation. Ensure compatibility with `onnxruntime-directml` for AMD GPUs on Windows or `onnxruntime-gpu` for NVIDIA GPUs.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/video_subtitle_translator.git
   cd video_subtitle_translator
   ```

2. **Create a Virtual Environment (Recommended):**

   ```bash
   python -m venv venv
   ```

   - **Activate the Virtual Environment:**
     - **Windows:**
       ```bash
       venv\Scripts\activate
       ```
     - **Unix or MacOS:**
       ```bash
       source venv/bin/activate
       ```

3. **Install Required Packages:**

   Ensure that you have `pip` updated:

   ```bash
   pip install --upgrade pip
   ```

   Install all dependencies:

   ```bash
   pip install torch openai-whisper srt transformers optimum[exporters] onnx onnxruntime-directml better_profanity numpy tqdm psutil GPUtil huggingface-hub
   ```

   > **Note:** 
   >
   > - Replace `onnxruntime-directml` with `onnxruntime` or `onnxruntime-gpu` based on your hardware and OS.
   > - For GPU support with NVIDIA CUDA, you might need to install `onnxruntime-gpu` instead.

4. **Hugging Face Authentication (If Needed):**

   Some models may require authentication. Log in using the Hugging Face CLI:

   ```bash
   huggingface-cli login
   ```

   Enter your Hugging Face access token when prompted.

## Exporting Translation Models to ONNX

Before running the translator, ensure that the MarianMT models for your desired language pairs are exported to ONNX format. This enhances performance and compatibility.

1. **Using the Provided Script:**

   The `video_subtitle_translator.py` script automatically handles exporting the required MarianMT models to ONNX if they aren't already present.

2. **Manual Export with `optimum-cli` (Optional):**

   Alternatively, you can manually export models using the `optimum-cli`. For example, to export the English-to-Vietnamese model:

   ```bash
   optimum-cli export onnx --model Helsinki-NLP/opus-mt-en-vi ./models/en-vi --task translation --opset 13 --for-ort
   ```

   **Parameters:**

   - `--model`: Model ID on Hugging Face or local path.
   - `./models/en-vi`: Output directory for the exported ONNX model.
   - `--task`: Specify the task (`translation` for MarianMT models).
   - `--opset`: ONNX opset version (default is 13).
   - `--for-ort`: Optimize the model for ONNX Runtime.

3. **Verify Exported Models:**

   Ensure the exported directory contains:

   - `encoder_model.onnx`
   - `decoder_model.onnx`

   MarianMT models do **not** require `decoder_with_past_model.onnx`.

## Usage

Run the `video_subtitle_translator.py` script with the appropriate arguments:

```bash
python video_subtitle_translator.py --video path_to_video.mp4 --source-lang vi --target-langs en --model-size base
```

**Arguments:**

- `--video`: **(Required)** Path to the input video file.
- `--source-lang`: **(Required)** Source language code (e.g., `en`, `vi`, `fr`).
- `--target-langs`: **(Required)** Target language codes (e.g., `de`, `it`, `jp`). Provide multiple codes separated by spaces.
- `--output-dir`: Directory to save subtitle files. Defaults to `subtitles`.
- `--model-size`: Whisper model size. Choices: `tiny`, `base`, `small`, `medium`, `large`. Defaults to `base`.
- `--model-dir`: Directory containing ONNX translation models. Defaults to `models`.
- `--base-cache-dir`: Base directory for caches. Defaults to `cache`.
- `--log-level`: Set the logging level. Choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Defaults to `INFO`.
- `--no-cache`: **(Optional)** Do not use cache for transcription and translation.

**Example:**

```bash
python video_subtitle_translator.py --video sample_video.mp4 --source-lang vi --target-langs en fr --model-size base --output-dir my_subtitles
```

## Caching Mechanism

To optimize performance, the script caches:

- **Transcriptions:** Stored in `cache/<video_hash>/transcript_cache.json`.
- **Translations:** Stored in `cache/<video_hash>/translation_cache.json`.

**Benefits:**

- **Speed:** Avoids redundant processing for repeated runs on the same video.
- **Efficiency:** Reduces computational load by reusing existing transcriptions and translations.

**Options:**

- Use the `--no-cache` flag to disable caching.

## Logging

The script maintains comprehensive logs to help monitor its operations and troubleshoot issues.

- **Log File:** `cache/<video_hash>/error.log`
- **Console Output:** Displays INFO level and above messages.

**Log Contents:**

- **INFO:** General information about the script's progress.
- **DEBUG:** Detailed debugging information (only if `--log-level DEBUG` is set).
- **ERROR/CRITICAL:** Logs errors and critical issues that may require attention.

## Troubleshooting

### 1. **ONNX Export Errors**

**Error:**

```
Error converting model 'Helsinki-NLP/opus-mt-vi-en': Module onnx is not installed!
```

**Solution:**

Ensure the `onnx` package is installed:

```bash
pip install onnx
```

### 2. **Missing `decoder_with_past_model.onnx`**

**Error:**

```
FileNotFoundError: Could not find any ONNX model file for the regex ['(.*)?decoder(.*)?with_past(.*)?\\.onnx'] in models\opus-mt-vi-en.
```

**Solution:**

MarianMT models do not use past key values. Ensure that:

- `use_cache=False` is set in the model's configuration before loading.
- The script correctly exports models without requiring `decoder_with_past_model.onnx`.

### 3. **ONNX Model Validation Warnings**

**Warning:**

```
The maximum absolute difference between the output of the reference model and the ONNX exported model is not within the set tolerance 1e-05:
- logits: max diff = 1.9550323486328125e-05.
```

**Solution:**

This indicates minor discrepancies between the original and ONNX models. If translation results are acceptable, this warning can be safely ignored. Otherwise, consider increasing the `atol` parameter during export or reviewing the export process.

### 4. **Whisper Model Warnings**

**Warning:**

```
UserWarning: FP16 is not supported on CPU; using FP32 instead
```

**Solution:**

Whisper models attempt to use FP16 precision, which isn't supported on CPU. This warning is informational and can be safely ignored. For faster performance, consider running on a GPU.

### 5. **Hugging Face Authentication Issues**

**Error:**

```
Failed to log in to Hugging Face: <error details>
```

**Solution:**

Ensure you're logged in using the Hugging Face CLI:

```bash
huggingface-cli login
```

Enter your access token when prompted.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository:**

   Click the "Fork" button at the top-right corner of the repository page.

2. **Create a Feature Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Commit Your Changes:**

   ```bash
   git commit -m "Add your descriptive commit message"
   ```

4. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

5. **Create a Pull Request:**

   Navigate to your forked repository and click the "New Pull Request" button.

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for powerful transcription capabilities.
- [Hugging Face Transformers](https://github.com/huggingface/transformers) for state-of-the-art translation models.
- [Hugging Face Optimum](https://github.com/huggingface/optimum) for ONNX model optimization.
- [MarianMT](https://huggingface.co/Helsinki-NLP) models by Helsinki-NLP for multilingual translation.

---

## Contact

For any questions or suggestions, please open an issue on the [GitHub repository](https://github.com/yourusername/video_subtitle_translator/issues) or contact [your.email@example.com](mailto:your.email@example.com).

```