import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from PIL import Image
import torch
from tqdm import tqdm

# Optional imports - will check availability
try:
    from transformers import Blip2Processor, Blip2ForConditionalGeneration
    BLIP2_AVAILABLE = True
except ImportError:
    BLIP2_AVAILABLE = False
    print("[WARNING] transformers not installed. Run: pip install transformers")


# CONFIGURATION

BASE_PATH = Path(__file__).parent.parent  # CEIPP folder
LLM_PATH = Path(__file__).parent  # LLM folder
DATASET_ROOT = BASE_PATH / "_21p1_pjirayu_Seed-Crystallization-Dataset" / "balanced_crystallization"
FILTER_OUTPUT = BASE_PATH / "Filter"
CAPTIONS_FILE = FILTER_OUTPUT / "all_captions_VER2.json"  # Captions from Filter folder
VERIFICATION_OUTPUT = LLM_PATH / "llm_verification_results"  # Output to LLM folder

# Model configurations - Using BLIP-2 Flan-T5 
MODEL_CONFIGS = {
    "blip2_small": {
        "name": "Salesforce/blip2-flan-t5-xl",
        "description": "BLIP-2 Flan-T5-XL float16 optimized (Best for Q&A, 6GB VRAM)",
        "vram_required": 6,
        "use_float16": True,
        "low_memory": True,
        "is_t5": True
    },
    "blip2_flan": {
        "name": "Salesforce/blip2-flan-t5-xl",
        "description": "BLIP-2 with FLAN-T5-XL (Instruction-tuned, best for Q&A)",
        "vram_required": 8,
        "is_t5": True
    },
    "blip2_flan_8bit": {
        "name": "Salesforce/blip2-flan-t5-xl",
        "description": "BLIP-2 Flan-T5-XL in 8-bit mode (Requires bitsandbytes)",
        "vram_required": 5,
        "load_in_8bit": True,
        "is_t5": True
    },
    "blip2_flan_xxl": {
        "name": "Salesforce/blip2-flan-t5-xxl",
        "description": "BLIP-2 with FLAN-T5-XXL (Most accurate, needs 16GB+ VRAM)",
        "vram_required": 16,
        "is_t5": True
    }
}

# PROMPTS

@dataclass
class VerificationPrompt:
    """Structure for verification prompts"""
    id: str
    prompt: str
    expected_response_type: str  # 'yes_no', 'classification', 'description', 'score'
    phase_specific: bool = False

# Prompts optimized for BLIP-2 Flan-T5 (instruction-tuned, follows Q&A format well)
# Flan-T5 is trained to follow instructions and answer questions directly
# UPDATED: Prompts designed for microscopic/industrial crystallization images
VERIFICATION_PROMPTS = [
    # 1. Phase correctness - Based on visual characteristics
    VerificationPrompt(
        id="phase_correct",
        prompt="Is this image showing a {expected_phase} state? Answer yes or no.",
        expected_response_type="yes_no",
        phase_specific=True
    ),
    
    # 2. Image type verification - More general question
    VerificationPrompt(
        id="caption_accurate",
        prompt="Is this a microscopic or scientific image? Answer yes or no.",
        expected_response_type="yes_no"
    ),
    
    # 3. Particle/crystal visibility check
    VerificationPrompt(
        id="info_correct",
        prompt="Are there visible particles or crystals in this image? Answer yes or no.",
        expected_response_type="yes_no"
    ),
    
    # 4. Particle clarity - Force number answer
    VerificationPrompt(
        id="crystal_clarity",
        prompt="How clear are the particles? Answer only 1, 2, 3, 4, or 5.",
        expected_response_type="score"
    ),
    
    # 5. Phase classification - Visual description based
    VerificationPrompt(
        id="phase_classification",
        prompt="Is this image: clear liquid, cloudy liquid, small particles, or large crystals? Answer one.",
        expected_response_type="classification"
    ),
    
    # 6. Visual description - Open ended
    VerificationPrompt(
        id="visual_characteristics",
        prompt="Describe what you see in this image in one sentence.",
        expected_response_type="description"
    ),
    
    # 7. Particle density estimation
    VerificationPrompt(
        id="growth_estimation",
        prompt="What percentage of the image has visible particles? Answer a number 0 to 100.",
        expected_response_type="score"
    ),
    
    # 8. Clarity level
    VerificationPrompt(
        id="growth_to_next_stage",
        prompt="Is the liquid clear or cloudy? Answer clear or cloudy.",
        expected_response_type="classification"
    ),
    
    # 9. Image quality - Force number
    VerificationPrompt(
        id="image_quality",
        prompt="Rate image sharpness. Answer only 1, 2, 3, 4, or 5.",
        expected_response_type="score"
    ),
    
    # 10. Content description
    VerificationPrompt(
        id="caption_completeness",
        prompt="What objects or substances are visible in this image?",
        expected_response_type="description"
    ),
    
    # 11. Image source verification
    VerificationPrompt(
        id="material_type",
        prompt="Is this a photograph or computer generated? Answer photo or generated.",
        expected_response_type="classification"
    ),
    
    # 12. Particle count estimation
    VerificationPrompt(
        id="crystal_count",
        prompt="How many particles are visible? Answer none, few, some, or many.",
        expected_response_type="classification"
    ),
    
    # 13. Overall quality score - Force number
    VerificationPrompt(
        id="overall_verification",
        prompt="Rate this image quality from 1 to 10. Answer only the number.",
        expected_response_type="score"
    )
]

# LLM VERIFICATION CLASS

class CrystallizationVerifier:
    """
    Vision-Language Model based verifier for crystallization captions.
    """
    
    def __init__(self, model_name: str = "blip2_opt", device: str = None):
        """
        Initialize the verifier with specified model.
        
        Args:
            model_name: Key from MODEL_CONFIGS or full HuggingFace model path
            device: 'cuda', 'cpu', or None for auto-detection
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.processor = None
        self.model_name = model_name
        
        print(f"[INFO] Using device: {self.device}")
        
    def load_model(self):
        """Load the BLIP-2 model and processor."""
        if not BLIP2_AVAILABLE:
            raise RuntimeError(
                "transformers library not available. "
                "Install with: pip install transformers accelerate"
            )
        
        model_config = MODEL_CONFIGS.get(self.model_name, {})
        model_path = model_config.get("name", self.model_name)
        use_8bit = model_config.get("load_in_8bit", False)
        low_memory = model_config.get("low_memory", False)
        use_float16 = model_config.get("use_float16", True)
        
        print(f"[INFO] Loading model: {model_path}")
        print(f"[INFO] Model config: {self.model_name}")
        if use_8bit:
            print(f"[INFO] Using 8-bit quantization")
        if low_memory:
            print(f"[INFO] Using low memory mode (optimized for 6GB VRAM)")
        
        # Clear GPU memory before loading
        if self.device == "cuda":
            torch.cuda.empty_cache()
            import gc
            gc.collect()
        
        try:
            # Load processor
            try:
                self.processor = Blip2Processor.from_pretrained(model_path, local_files_only=True)
                print("[INFO] Using cached processor")
            except Exception:
                print("[INFO] Downloading processor...")
                self.processor = Blip2Processor.from_pretrained(model_path)
            
            # Check if 8-bit loading is requested
            if use_8bit:
                try:
                    from transformers import BitsAndBytesConfig
                    quantization_config = BitsAndBytesConfig(load_in_8bit=True)
                    try:
                        self.model = Blip2ForConditionalGeneration.from_pretrained(
                            model_path,
                            quantization_config=quantization_config,
                            device_map="auto",
                            local_files_only=True
                        )
                        print("[INFO] Using cached model (8-bit)")
                    except Exception:
                        print("[INFO] Downloading model (8-bit)...")
                        self.model = Blip2ForConditionalGeneration.from_pretrained(
                            model_path,
                            quantization_config=quantization_config,
                            device_map="auto"
                        )
                except ImportError:
                    print("[WARNING] bitsandbytes not installed. Install with: pip install bitsandbytes")
                    print("[INFO] Falling back to float16 mode")
                    use_8bit = False
                    low_memory = True  # Try low memory mode instead
                except Exception as e:
                    print(f"[WARNING] 8-bit loading failed: {e}")
                    print("[INFO] Falling back to float16 mode")
                    use_8bit = False
                    low_memory = True
            
            # Low memory mode for 6GB VRAM (using float16 + memory optimization)
            if not use_8bit and low_memory and self.device == "cuda":
                print("[INFO] Loading with float16 + low memory optimization...")
                try:
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_path,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        low_cpu_mem_usage=True,
                        local_files_only=True
                    )
                    print("[INFO] Using cached model (float16 optimized)")
                except Exception:
                    print("[INFO] Downloading model (float16 optimized)...")
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_path,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        low_cpu_mem_usage=True
                    )
            elif not use_8bit:
                # Standard loading
                dtype = torch.float16 if (self.device == "cuda" and use_float16) else torch.float32
                try:
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_path,
                        torch_dtype=dtype,
                        device_map="auto" if self.device == "cuda" else None,
                        local_files_only=True
                    )
                    print("[INFO] Using cached model")
                except Exception:
                    print("[INFO] Downloading model...")
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_path,
                        torch_dtype=dtype,
                        device_map="auto" if self.device == "cuda" else None
                    )
            
            if self.device == "cpu" and not use_8bit:
                self.model = self.model.to(self.device)
            
            # Set model to eval mode
            self.model.eval()
            
            # Clear cache after loading
            if self.device == "cuda":
                torch.cuda.empty_cache()
                
            print(f"[OK] Model loaded successfully")
            
            # Print VRAM usage
            if self.device == "cuda":
                allocated = torch.cuda.memory_allocated() / 1024**3
                reserved = torch.cuda.memory_reserved() / 1024**3
                print(f"[INFO] VRAM allocated: {allocated:.2f}GB, reserved: {reserved:.2f}GB")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_response(
        self, 
        image: Image.Image, 
        prompt: str, 
        max_new_tokens: int = 50
    ) -> str:
        """
        Generate response from the model for a given image and prompt.
        Flan-T5 is encoder-decoder so it outputs only the answer (no echo).
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Prepare inputs
        inputs = self.processor(
            images=image, 
            text=prompt, 
            return_tensors="pt"
        )
        
        # Move to device
        if self.device == "cuda":
            inputs = {k: v.to(self.device, dtype=torch.float16) if v.dtype == torch.float32 else v.to(self.device) 
                     for k, v in inputs.items()}
        else:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate with settings optimized for BLIP-2 Flan-T5 (encoder-decoder, no echo issue)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                min_new_tokens=1,
                do_sample=False,  # Greedy for more consistent answers
                num_beams=3,  # Beam search for better quality
                length_penalty=1.0,
                repetition_penalty=2.0,  # Prevent repetition (1.0 = no penalty)
                no_repeat_ngram_size=3,  # Never repeat 3-grams
                early_stopping=True,  # Stop when all beams are done
            )
        
        # Flan-T5 is encoder-decoder, output is just the answer (no prompt echo)
        response = self.processor.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up common patterns
        response = response.strip()
        
        # Remove any remaining echo of the question
        for prefix in ["Answer:", "Response:", "A:"]:
            if response.lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()
        
        # Clean up to free VRAM
        del inputs, outputs
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        return response if response else "no response"
    
    def verify_caption(
        self, 
        image_path: str, 
        caption_data: Dict,
        prompts_to_use: List[str] = None
    ) -> Dict:
        """
        Verify a single caption against its image using multiple prompts.
        
        Args:
            image_path: Path to the image file
            caption_data: Dictionary containing caption and metadata
            prompts_to_use: List of prompt IDs to use (None = all prompts)
            
        Returns:
            Dictionary with verification results
        """
        # Load image
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to load image: {e}",
                "image_path": image_path
            }
        
        # Select prompts
        prompts = VERIFICATION_PROMPTS
        if prompts_to_use:
            prompts = [p for p in VERIFICATION_PROMPTS if p.id in prompts_to_use]
        
        # Run verification
        results = {
            "image_path": image_path,
            "image_name": caption_data.get("image", ""),
            "expected_phase": caption_data.get("phase", ""),
            "expected_caption": caption_data.get("initial_caption", ""),
            "verification_results": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for prompt_config in prompts:
            # Format prompt with caption data (including growth_percentage for cross-validation)
            prompt_text = prompt_config.prompt.format(
                expected_phase=caption_data.get("phase", "unknown"),
                caption=caption_data.get("initial_caption", ""),
                growth_percentage=caption_data.get("growth_percentage", "unknown")
            )
            
            try:
                response = self.generate_response(image, prompt_text)
                results["verification_results"][prompt_config.id] = {
                    "prompt": prompt_text,
                    "response": response,
                    "response_type": prompt_config.expected_response_type,
                    "status": "success"
                }
            except Exception as e:
                results["verification_results"][prompt_config.id] = {
                    "prompt": prompt_text,
                    "response": None,
                    "response_type": prompt_config.expected_response_type,
                    "status": "error",
                    "error": str(e)
                }
        
        # Calculate overall verification score
        results["verification_summary"] = self._summarize_verification(results["verification_results"])
        
        return results
    
    def _summarize_verification(self, verification_results: Dict) -> Dict:
        """Summarize verification results into overall metrics."""
        summary = {
            "total_prompts": len(verification_results),
            "successful_prompts": sum(1 for v in verification_results.values() if v.get("status") == "success"),
            "phase_match": None,
            "caption_accurate": None,
            "crystal_clarity_score": None,
            "predicted_phase": None,
            "growth_to_next_stage": None,
            "overall_score": None,
            "needs_review": False,
            "confidence_level": "unknown"
        }
        
        # Extract specific results
        for prompt_id, result in verification_results.items():
            if result.get("status") != "success":
                continue
                
            response = result.get("response", "").lower().strip()
            
            if prompt_id == "phase_correct":
                summary["phase_match"] = "yes" in response
                # Don't set needs_review just for phase mismatch - it's informational
                    
            elif prompt_id == "caption_accurate":
                # Now asking "Is this a microscopic or scientific image?"
                summary["caption_accurate"] = "yes" in response
                # Don't set needs_review - this is less critical now
                    
            elif prompt_id == "crystal_clarity":
                # Try to extract score (1-5)
                import re
                numbers = re.findall(r'\b([1-5])\b', response)
                if numbers:
                    summary["crystal_clarity_score"] = int(numbers[0])
                        
            elif prompt_id == "phase_classification":
                # Map visual descriptions to phases
                if "clear liquid" in response or "clear" in response:
                    summary["predicted_phase"] = "unsaturated"
                elif "cloudy" in response or "small particle" in response:
                    summary["predicted_phase"] = "labile"
                elif "particle" in response or "forming" in response:
                    summary["predicted_phase"] = "intermediate"
                elif "large" in response or "crystal" in response:
                    summary["predicted_phase"] = "metastable"
                # Also check for direct phase names
                for phase in ["unsaturated", "labile", "intermediate", "metastable"]:
                    if phase in response:
                        summary["predicted_phase"] = phase
                        break
            
            elif prompt_id == "growth_to_next_stage":
                # Now asking "Is the liquid clear or cloudy?"
                summary["liquid_clarity"] = response
            
            elif prompt_id == "overall_verification":
                # Extract overall score (1-10)
                import re
                scores = re.findall(r'\b([1-9]|10)\b', response)
                if scores:
                    summary["overall_score"] = int(scores[0])
            
            elif prompt_id == "info_correct":
                # Particles visible?
                summary["particles_visible"] = "yes" in response
            
            elif prompt_id == "crystal_count":
                # Map to count category
                summary["particle_count"] = response
        
        # NEW: Improved confidence calculation
        # Focus on visual consistency rather than domain-specific terms
        confidence_points = 0
        
        # Phase match is important (2 points)
        if summary["phase_match"]:
            confidence_points += 2
        
        # Scientific image detection (1 point) - less weight now
        if summary["caption_accurate"]:
            confidence_points += 1
        
        # Overall score (2 points if good)
        if summary["overall_score"]:
            if summary["overall_score"] >= 7:
                confidence_points += 2
            elif summary["overall_score"] >= 5:
                confidence_points += 1
        
        # Crystal clarity (1 point)
        if summary["crystal_clarity_score"] and summary["crystal_clarity_score"] >= 3:
            confidence_points += 1
        
        # Particles visible consistency (1 point)
        if summary.get("particles_visible") is not None:
            confidence_points += 1
            
        # Determine confidence level (max 8 points now)
        if confidence_points >= 5:
            summary["confidence_level"] = "high"
            summary["needs_review"] = False
        elif confidence_points >= 3:
            summary["confidence_level"] = "medium"
            summary["needs_review"] = False  # Medium is acceptable
        else:
            summary["confidence_level"] = "low"
            summary["needs_review"] = True  # Only low confidence needs review
            
        return summary

# BATCH VERIFICATION

def run_batch_verification(
    captions_file: str = None,
    output_dir: str = None,
    model_name: str = "blip2_opt",
    sample_size: int = None,
    prompts_to_use: List[str] = None,
    resume: bool = True
) -> Tuple[List[Dict], Dict]:
    """
    Run verification on a batch of captions with checkpoint/resume support.
    
    Args:
        captions_file: Path to JSON file with captions
        output_dir: Directory for output files
        model_name: Model to use for verification
        sample_size: Number of samples to process (None = all)
        prompts_to_use: List of prompt IDs (None = all prompts)
        resume: If True, resume from last checkpoint (default: True)
        
    Returns:
        Tuple of (verification results list, statistics dict)
    """
    captions_file = Path(captions_file or CAPTIONS_FILE)
    output_dir = Path(output_dir or VERIFICATION_OUTPUT)
    os.makedirs(output_dir, exist_ok=True)
    
    # Checkpoint file for resuming
    checkpoint_file = output_dir / "verification_checkpoint.json"
    results_file = output_dir / "verification_results.json"
    
    print("=" * 80)
    print("LLM Verification Pipeline - Crystallization Caption Cross-Validation")
    print("=" * 80)
    
    # Load captions
    if not captions_file.exists():
        print(f"[ERROR] Captions file not found: {captions_file}")
        print("[INFO] Please run generate_captions_enhanced.py first.")
        return [], {}
    
    with open(captions_file, 'r', encoding='utf-8') as f:
        captions = json.load(f)
    
    print(f"[INFO] Loaded {len(captions)} captions")
    
    # Check for existing checkpoint to resume
    results = []
    processed_images = set()
    start_index = 0
    
    if resume and checkpoint_file.exists():
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            # Load existing results
            if results_file.exists():
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            
            processed_images = set(checkpoint.get("processed_images", []))
            start_index = checkpoint.get("last_index", 0)
            
            print(f"[INFO] Resuming from checkpoint: {len(processed_images)} images already processed")
            print(f"[INFO] Continuing from index {start_index}...")
        except Exception as e:
            print(f"[WARNING] Failed to load checkpoint: {e}")
            print("[INFO] Starting fresh...")
            results = []
            processed_images = set()
            start_index = 0
    
    # Sample if needed (only for fresh starts)
    if sample_size and sample_size < len(captions) and not processed_images:
        import random
        captions = random.sample(captions, sample_size)
        print(f"[INFO] Sampled {sample_size} captions for verification")
    
    # Filter out already processed images
    remaining_captions = []
    for i, caption in enumerate(captions):
        image_name = caption.get("image", "")
        if image_name not in processed_images:
            remaining_captions.append((i, caption))
    
    if not remaining_captions:
        print("[INFO] All images already verified!")
        return results, {}
    
    print(f"[INFO] {len(remaining_captions)} images remaining to verify")
    
    # Initialize verifier
    verifier = CrystallizationVerifier(model_name=model_name)
    
    if not verifier.load_model():
        print("[ERROR] Failed to load model. Exiting.")
        return [], {}
    
    # Run verification
    statistics = {
        "total_processed": len(processed_images),
        "successful": 0,
        "errors": 0,
        "by_phase": {},
        "phase_match_rate": 0,
        "caption_accuracy_rate": 0,
        "needs_review_count": 0
    }
    
    print(f"\n[INFO] Starting verification of {len(remaining_captions)} images...")
    print("[INFO] Press Ctrl+C to pause (progress will be saved)")
    print("-" * 80)
    
    try:
        for idx, (original_idx, caption_data) in enumerate(tqdm(remaining_captions, desc="Verifying")):
            image_path = caption_data.get("image_path")
            image_name = caption_data.get("image", "")
            
            if not image_path or not Path(image_path).exists():
                # Try to reconstruct path
                material = caption_data.get("category_id", "")
                phase = caption_data.get("phase", "")
                image_path = DATASET_ROOT / material / phase / image_name
            
            if not Path(image_path).exists():
                statistics["errors"] += 1
                continue
            
            result = verifier.verify_caption(
                str(image_path),
                caption_data,
                prompts_to_use
            )
            
            results.append(result)
            processed_images.add(image_name)
            statistics["total_processed"] += 1
            
            if result.get("verification_summary", {}).get("phase_match"):
                statistics["successful"] += 1
                
            if result.get("verification_summary", {}).get("needs_review"):
                statistics["needs_review_count"] += 1
            
            # Track by phase
            phase = caption_data.get("phase", "unknown")
            if phase not in statistics["by_phase"]:
                statistics["by_phase"][phase] = {"total": 0, "phase_match": 0, "caption_accurate": 0}
            statistics["by_phase"][phase]["total"] += 1
            
            if result.get("verification_summary", {}).get("phase_match"):
                statistics["by_phase"][phase]["phase_match"] += 1
            if result.get("verification_summary", {}).get("caption_accurate"):
                statistics["by_phase"][phase]["caption_accurate"] += 1
            
            # Save checkpoint every 10 images
            if (idx + 1) % 10 == 0:
                _save_checkpoint(checkpoint_file, results_file, results, processed_images, original_idx)
    
    except KeyboardInterrupt:
        print("\n\n[PAUSED] Verification paused by user.")
        print("[INFO] Saving checkpoint...")
        _save_checkpoint(checkpoint_file, results_file, results, processed_images, original_idx)
        print(f"[INFO] Progress saved: {len(processed_images)}/{len(captions)} images")
        print("[INFO] Run the same command again to resume.")
        return results, statistics
    
    # Calculate rates
    if statistics["total_processed"] > 0:
        phase_matches = sum(1 for r in results 
                          if r.get("verification_summary", {}).get("phase_match"))
        caption_matches = sum(1 for r in results 
                             if r.get("verification_summary", {}).get("caption_accurate"))
        
        statistics["phase_match_rate"] = phase_matches / statistics["total_processed"]
        statistics["caption_accuracy_rate"] = caption_matches / statistics["total_processed"]
    
    # Save final results
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Results saved to: {results_file}")
    
    stats_file = output_dir / "verification_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, indent=2, ensure_ascii=False)
    print(f"[OK] Statistics saved to: {stats_file}")
    
    # Save items needing review
    review_items = [r for r in results if r.get("verification_summary", {}).get("needs_review")]
    if review_items:
        review_file = output_dir / "needs_review.json"
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review_items, f, indent=2, ensure_ascii=False)
        print(f"[OK] Items needing review saved to: {review_file}")
    
    # Remove checkpoint file when complete
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        print("[OK] Checkpoint cleared (verification complete)")
    
    # Print summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Total Processed: {statistics['total_processed']}")
    print(f"Phase Match Rate: {statistics['phase_match_rate']:.1%}")
    print(f"Caption Accuracy Rate: {statistics['caption_accuracy_rate']:.1%}")
    print(f"Items Needing Review: {statistics['needs_review_count']}")
    
    return results, statistics


def _save_checkpoint(checkpoint_file, results_file, results, processed_images, last_index):
    """Save checkpoint for resume functionality."""
    # Save results so far
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save checkpoint info
    checkpoint = {
        "processed_images": list(processed_images),
        "last_index": last_index,
        "timestamp": datetime.now().isoformat(),
        "total_processed": len(processed_images)
    }
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)

# QUICK VERIFICATION (Without full model loading)

def generate_verification_prompts_only(
    captions_file: str = None,
    output_dir: str = None
) -> Dict:
    """
    Generate verification prompts for all captions without running the model.
    Useful for preparing batch processing or manual review.
    """
    captions_file = Path(captions_file or CAPTIONS_FILE)
    output_dir = Path(output_dir or VERIFICATION_OUTPUT)
    
    if not captions_file.exists():
        print(f"[ERROR] Captions file not found: {captions_file}")
        return {}
    
    with open(captions_file, 'r', encoding='utf-8') as f:
        captions = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate prompts for each caption
    all_prompts = []
    
    for caption_data in captions:
        image_prompts = {
            "image": caption_data.get("image", ""),
            "image_path": caption_data.get("image_path", ""),
            "phase": caption_data.get("phase", ""),
            "prompts": []
        }
        
        for prompt_config in VERIFICATION_PROMPTS:
            formatted_prompt = prompt_config.prompt.format(
                expected_phase=caption_data.get("phase", "unknown"),
                caption=caption_data.get("initial_caption", "")
            )
            
            image_prompts["prompts"].append({
                "id": prompt_config.id,
                "prompt": formatted_prompt,
                "response_type": prompt_config.expected_response_type
            })
        
        all_prompts.append(image_prompts)
    
    # Save prompts
    prompts_file = output_dir / "verification_prompts_prepared.json"
    with open(prompts_file, 'w', encoding='utf-8') as f:
        json.dump(all_prompts, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Verification prompts saved to: {prompts_file}")
    print(f"[INFO] Total images: {len(all_prompts)}")
    print(f"[INFO] Prompts per image: {len(VERIFICATION_PROMPTS)}")
    
    return {"prompts_file": str(prompts_file), "total_images": len(all_prompts)}

# MAIN

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="LLM Verification for Crystallization Captions"
    )
    parser.add_argument(
        "--mode", 
        choices=["verify", "prompts_only"],
        default="prompts_only",
        help="Mode: 'verify' runs full verification, 'prompts_only' generates prompts without model"
    )
    parser.add_argument(
        "--model",
        default="blip2_opt",
        help="Model to use (blip2_opt, blip2_flan, blip2_opt_6.7b)"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Number of samples to verify (default: all)"
    )
    parser.add_argument(
        "--captions",
        default=None,
        help="Path to captions JSON file"
    )
    
    args = parser.parse_args()
    
    if args.mode == "verify":
        run_batch_verification(
            captions_file=args.captions,
            model_name=args.model,
            sample_size=args.sample
        )
    else:
        generate_verification_prompts_only(captions_file=args.captions)

if __name__ == "__main__":
    main()
