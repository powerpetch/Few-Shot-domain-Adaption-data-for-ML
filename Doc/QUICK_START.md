# Quick Start Guide: Sugar Crystallization Image Captioning Project

## Overview
This guide helps you quickly set up and run the image captioning pipeline for your sugar crystallization dataset.

---

## 📋 Prerequisites

### Software Requirements
- Python 3.8+
- GPU (optional, for faster processing)
- 4GB+ RAM minimum

### Accounts & API Keys
- **OpenAI Account** (for GPT-4 Vision) - Get key from https://platform.openai.com/api-keys
- **OR Anthropic Account** (for Claude 3) - Get key from https://console.anthropic.com/

### Dataset
- Images should be organized in phase subdirectories:
  ```
  d:\user\CEIPP\balanced_crystallization\phy_sugar_db\
    ├── unsaturated/
    ├── labile/
    ├── intermediate/
    └── metastable/
  ```

---

## 🚀 Getting Started (3 Steps)

### Step 1: Install Dependencies
```bash
cd d:\user\CEIPP
pip install openai anthropic pillow opencv-python pandas matplotlib
```

### Step 2: Set Environment Variable
Replace `YOUR_API_KEY_HERE` with your actual key.

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
# OR
$env:ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
```

**Windows Command Prompt:**
```cmd
set OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
REM OR
set ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
# OR
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
```

### Step 3: Run the Pipeline

#### Option A: Command Line (Batch Processing)
```bash
python d:\user\CEIPP\LLM\captioning_pipeline.py \
  --input_dir "d:\user\CEIPP\balanced_crystallization\phy_sugar_db" \
  --output_dir "d:\user\CEIPP\annotations" \
  --provider openai
```

#### Option B: Interactive Jupyter Notebook (Recommended)
```bash
cd d:\user\CEIPP\LLM
jupyter notebook captioning_interactive.ipynb
```

Then run cells sequentially, following the prompts.

---

## 📊 Understanding the Workflow

### Phase 1: Dataset Exploration
- Scans dataset structure
- Counts images per phase
- Creates distribution visualization

### Phase 2: LLM Configuration
- Sets up connection to API
- Tests connection
- Validates API key

### Phase 3: Caption Generation
- Processes images one by one
- Sends to multi-modal LLM
- Stores generated captions

### Phase 4: Validation
- Calculates quality metrics
- Checks consistency
- Flags problematic captions

### Phase 5: Output
- Saves JSON annotations
- Creates CSV for easy viewing
- Generates visualizations

---

## 📁 Output Files

After running the pipeline, you'll get:

```
d:\user\CEIPP\annotations\
├── captions.json                    # All generated captions
├── annotated_dataset.json           # Complete annotated dataset
├── annotated_dataset.csv            # CSV version for Excel
├── quality_metrics.json             # Quality statistics
├── dataset_distribution.png         # Chart of image counts
└── sample_images_with_captions.png  # Visual samples
```

---

## 🔧 Configuration Options

### For Command Line:
```bash
python captioning_pipeline.py \
  --input_dir PATH_TO_IMAGES \
  --output_dir PATH_TO_OUTPUT \
  --provider {openai|anthropic} \
  --api_key YOUR_KEY_HERE \
  --sample_size 50  # Process first 50 images only (for testing)
```

### For Jupyter Notebook:
Edit these variables in cell 2:
```python
LLM_PROVIDER = "openai"  # Change to "anthropic" if needed
images_per_phase = 2     # Increase to process more images
BASE_DIR = Path(r"d:\user\CEIPP")  # Adjust if needed
```

---

## 💰 Cost Estimation

### OpenAI GPT-4 Vision Pricing (as of 2025)
- Input: $0.01 per 1K tokens
- Output: $0.03 per 1K tokens
- Per image: ~$0.02-0.05 (estimated)

**Example Costs:**
- 100 images: ~$2-5
- 500 images: ~$10-25
- 1000 images: ~$20-50

### Anthropic Claude 3 Opus Pricing
- Input: $0.015 per 1K tokens
- Output: $0.075 per 1K tokens
- Per image: ~$0.05-0.10 (estimated)

**Cost-Saving Tips:**
- Test with `sample_size` parameter first
- Process in batches and monitor costs
- Use cheaper models for testing (GPT-4 mini if available)

---

## 🐛 Troubleshooting

### Issue: "API key not found"
**Solution:**
1. Verify environment variable is set: `echo %OPENAI_API_KEY%` (Windows)
2. Check API key is valid on provider website
3. Restart terminal/IDE after setting environment variable

### Issue: "Image file not found"
**Solution:**
1. Verify dataset path is correct
2. Check images are in subdirectories (unsaturated/, labile/, etc.)
3. Verify image format (JPG, PNG, JPEG)

### Issue: "Rate limit exceeded"
**Solution:**
1. Reduce `sample_size` or `images_per_phase`
2. Wait a few minutes before retrying
3. Check API usage on provider dashboard
4. Consider using batch API for large datasets

### Issue: "Out of memory"
**Solution:**
1. Process fewer images at once
2. Close other applications
3. Increase virtual memory
4. Use cloud GPU if available

### Issue: "Poor quality captions"
**Solution:**
1. Adjust the system prompt in the code
2. Try different LLM provider
3. Provide more context in the prompt
4. Manually review and correct captions

---

## ✅ Quality Checklist

Before using the captions for training, verify:
- [ ] All images have captions
- [ ] Phase labels match actual image content
- [ ] Growth percentages are reasonable
- [ ] Technical terminology is correct
- [ ] No empty or duplicate captions
- [ ] JSON files are valid and parseable
- [ ] CSV file can be opened in Excel
- [ ] Visual samples look good

---

## 📚 Understanding the Output

### captions.json Format
```json
[
  {
    "image_path": "d:\\user\\CEIPP\\balanced_crystallization\\phy_sugar_db\\unsaturated\\image_001.jpg",
    "phase_label": "unsaturated",
    "generated_caption": "UNSATURATED: Clear, transparent sugar solution...",
    "model": "gpt-4-vision",
    "provider": "openai",
    "timestamp": "2025-12-18T10:30:45.123456"
  },
  ...
]
```

### annotated_dataset.csv Format
| Image | Phase | Growth Range | Caption |
|-------|-------|--------------|---------|
| image_001.jpg | unsaturated | 0% | UNSATURATED: Clear, transparent sugar solution... |
| image_002.jpg | labile | 5-15% | LABILE: Very small crystal nuclei... |
| image_003.jpg | intermediate | 15-50% | INTERMEDIATE: Visible crystal growth... |
| image_004.jpg | metastable | 50-100% | METASTABLE: Well-developed crystals... |

---

## 🎯 Next Steps After Caption Generation

1. **Validate Captions**
   - Use `CAPTION_VALIDATION_CHECKLIST.md`
   - Review samples manually
   - Correct errors

2. **Create Training Dataset**
   - Split into train/val/test (80/10/10)
   - Create PyTorch datasets
   - Prepare for model training

3. **Train Model**
   - Use Vision Transformer or CNN
   - Fine-tune with captions
   - Evaluate performance

4. **Deploy**
   - Create inference script
   - Package as API/web service
   - Monitor performance

---

## 📖 Documentation References

- **Project Guide:** `PROJECT_GUIDE.md` - Full project overview
- **Validation Checklist:** `CAPTION_VALIDATION_CHECKLIST.md` - Quality criteria
- **Python Script:** `captioning_pipeline.py` - Command-line tool
- **Jupyter Notebook:** `captioning_interactive.ipynb` - Interactive interface

---

## 🆘 Getting Help

### Common Questions:

**Q: Can I use different LLM providers?**  
A: Yes! The pipeline supports OpenAI and Anthropic. You can modify it to support others.

**Q: What if my images are not organized by phase?**  
A: Manually organize them first, or modify the script to accept flat directories.

**Q: Can I use this locally without API calls?**  
A: Yes! Use open-source models like LLaVA or BLIP-2, but you'll need GPU.

**Q: How long does it take to process all images?**  
A: ~30-60 seconds per image depending on LLM provider and network speed.

**Q: Can I combine captions from multiple LLMs?**  
A: Yes! The notebook supports this - generate with different providers and compare.

---

## 📞 Support

For issues:
1. Check the troubleshooting section above
2. Review full `PROJECT_GUIDE.md`
3. Check LLM provider documentation
4. Look at generated error messages carefully

---

**Version:** 1.0  
**Last Updated:** 2025-12-18  
**Status:** Ready to Use
