"""
BLIP-2 Test Script for Crystallization Images
==============================================
This script demonstrates how to use BLIP-2 to analyze crystallization images.

Usage:
    python test_blip2.py --image_path <path_to_image>
    python test_blip2.py  # Uses sample image from dataset
"""

import torch
from PIL import Image
from pathlib import Path
import sys

# Check GPU availability
print("=" * 60)
print("BLIP-2 Environment Check")
print("=" * 60)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("[WARNING] No GPU detected. BLIP-2 will run on CPU (very slow!)")
print("=" * 60)

# Import transformers
try:
    from transformers import Blip2Processor, Blip2ForConditionalGeneration
    print("[OK] Transformers imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import transformers: {e}")
    print("Install with: pip install transformers accelerate")
    sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Model options (choose one)
MODEL_OPTIONS = {
    "small": "Salesforce/blip2-opt-2.7b",      # ~8GB VRAM
    "medium": "Salesforce/blip2-flan-t5-xl",   # ~10GB VRAM  
    "large": "Salesforce/blip2-opt-6.7b"       # ~16GB VRAM
}

# You can force a specific model here (override auto-selection)
FORCE_MODEL = None  # Set to "small", "medium", or "large" to override

# Choose model based on available VRAM
if FORCE_MODEL:
    MODEL_NAME = MODEL_OPTIONS[FORCE_MODEL]
    print(f"[INFO] Forced model: {FORCE_MODEL}")
elif torch.cuda.is_available():
    vram = torch.cuda.get_device_properties(0).total_memory / 1e9
    if vram >= 16:
        MODEL_NAME = MODEL_OPTIONS["large"]
    elif vram >= 10:
        MODEL_NAME = MODEL_OPTIONS["medium"]
    else:
        MODEL_NAME = MODEL_OPTIONS["small"]
else:
    MODEL_NAME = MODEL_OPTIONS["small"]  # CPU mode

# 8-bit quantization mode (allows larger models on smaller VRAM)
USE_8BIT = False  # Set to True to enable 8-bit quantization for large model on low VRAM

print(f"[INFO] Selected model: {MODEL_NAME}")

# =============================================================================
# LOAD MODEL
# =============================================================================

def load_model():
    """Load BLIP-2 model and processor."""
    print(f"\n[INFO] Loading model: {MODEL_NAME}")
    print("[INFO] This may take a few minutes on first run (downloading model)...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    processor = Blip2Processor.from_pretrained(MODEL_NAME)
    
    # Use 8-bit quantization if enabled (for large models on small VRAM)
    if USE_8BIT and device == "cuda":
        try:
            from transformers import BitsAndBytesConfig
            print("[INFO] Using 8-bit quantization mode")
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            model = Blip2ForConditionalGeneration.from_pretrained(
                MODEL_NAME,
                quantization_config=quantization_config,
                device_map="auto"
            )
        except ImportError:
            print("[WARNING] bitsandbytes not installed. Run: pip install bitsandbytes")
            print("[INFO] Falling back to float16 mode")
            model = Blip2ForConditionalGeneration.from_pretrained(
                MODEL_NAME,
                torch_dtype=dtype,
                device_map="auto"
            )
    else:
        model = Blip2ForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            torch_dtype=dtype,
            device_map="auto" if device == "cuda" else None
        )
    
    if device == "cpu":
        model = model.to(device)
    
    print(f"[OK] Model loaded on {device}")
    return model, processor, device

# =============================================================================
# INFERENCE FUNCTIONS
# =============================================================================

def ask_about_image(model, processor, image_path: str, question: str, device: str) -> str:
    """
    Ask a question about an image using BLIP-2.
    
    Args:
        model: BLIP-2 model
        processor: BLIP-2 processor
        image_path: Path to image file
        question: Question to ask about the image
        device: 'cuda' or 'cpu'
    
    Returns:
        Model's response as string
    """
    # Load and prepare image
    image = Image.open(image_path).convert("RGB")
    
    # Prepare prompt (BLIP-2 format)
    prompt = f"Question: {question} Answer:"
    
    # Process inputs
    inputs = processor(images=image, text=prompt, return_tensors="pt")
    
    # Move to device
    if device == "cuda":
        inputs = {k: v.to(device, dtype=torch.float16) if v.dtype == torch.float32 else v.to(device) 
                 for k, v in inputs.items()}
    else:
        inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            num_beams=3
        )
    
    # Decode and return
    response = processor.decode(outputs[0], skip_special_tokens=True)
    return response.strip()

def generate_caption(model, processor, image_path: str, device: str) -> str:
    """Generate a caption for an image (no question, just describe)."""
    image = Image.open(image_path).convert("RGB")
    
    inputs = processor(images=image, return_tensors="pt")
    
    if device == "cuda":
        inputs = {k: v.to(device, dtype=torch.float16) if v.dtype == torch.float32 else v.to(device) 
                 for k, v in inputs.items()}
    else:
        inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=50)
    
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption.strip()

# =============================================================================
# CRYSTALLIZATION-SPECIFIC QUESTIONS
# =============================================================================

CRYSTALLIZATION_QUESTIONS = [
    # Phase classification
    "What crystallization phase is shown? Options: unsaturated, labile, intermediate, or metastable.",
    
    # Crystal visibility
    "Are crystals visible in this image? Rate from 1 to 5.",
    
    # Crystal characteristics
    "Describe the crystals you see - their size, shape, and density.",
    
    # Growth estimation
    "Estimate the crystal growth percentage from 0% to 100%.",
    
    # Background
    "How much background is visible? Answer: all, most, half, little, or none.",
    
    # Image type
    "Is this a real microscope image or a computer simulation?"
]

# =============================================================================
# MAIN TEST
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test BLIP-2 on crystallization images")
    parser.add_argument("--image_path", type=str, default=None, help="Path to image")
    parser.add_argument("--question", type=str, default=None, help="Custom question")
    args = parser.parse_args()
    
    # Find sample image if not provided
    if args.image_path is None:
        base_path = Path(__file__).parent.parent
        dataset_path = base_path / "_21p1_pjirayu_Seed-Crystallization-Dataset" / "balanced_crystallization"
        
        # Try to find a sample image
        sample_paths = [
            dataset_path / "phy_sugar_db" / "intermediate" / "1.jpg",
            dataset_path / "phy_sugar_db" / "labile" / "1.jpg",
            dataset_path / "phy_sugar_opr" / "metastable" / "1.jpg",
        ]
        
        for path in sample_paths:
            if path.exists():
                args.image_path = str(path)
                break
        
        if args.image_path is None:
            print("[ERROR] No sample image found. Please provide --image_path")
            return
    
    print(f"\n[INFO] Using image: {args.image_path}")
    
    # Load model
    model, processor, device = load_model()
    
    # Test 1: Generate caption
    print("\n" + "=" * 60)
    print("TEST 1: Generate Caption")
    print("=" * 60)
    caption = generate_caption(model, processor, args.image_path, device)
    print(f"Caption: {caption}")
    
    # Test 2: Ask crystallization questions
    print("\n" + "=" * 60)
    print("TEST 2: Crystallization Questions")
    print("=" * 60)
    
    questions = CRYSTALLIZATION_QUESTIONS if args.question is None else [args.question]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = ask_about_image(model, processor, args.image_path, q, device)
        print(f"A: {answer}")
    
    print("\n" + "=" * 60)
    print("[DONE] Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
