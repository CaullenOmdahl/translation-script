# test_model.py

import sys
from load_model import load_translation_model

def test_model(model_dir):
    model, tokenizer = load_translation_model(model_dir)
    # Sample translation
    input_text = "Xin chào, bạn khỏe không?"
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=50, use_cache=False)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Original: {input_text}")
    print(f"Translated: {translated_text}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_model.py <model_dir>")
        print("Example: python test_model.py models/opus-mt-vi-en")
        sys.exit(1)
    
    model_dir = sys.argv[1]
    test_model(model_dir)
