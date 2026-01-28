# 📑 Project Index & File Guide

## Quick Navigation

### 🎯 Getting Started
- **New to this project?** → Start here: [QUICK_START.md](QUICK_START.md)
- **Want full details?** → Read: [PROJECT_GUIDE.md](PROJECT_GUIDE.md)
- **Need overview?** → See: [README.md](README.md)

---

## 📂 Complete File Structure

### Root Level Documentation
```
d:\user\CEIPP\
│
├── README.md ⭐
│   └─ Project overview, quick links, learning paths
│
├── PROJECT_GUIDE.md ⭐⭐⭐
│   └─ Complete methodology, phase explanations, workflow
│
├── QUICK_START.md ⭐⭐
│   └─ 3-step setup, troubleshooting, configuration
│
├── requirements.txt
│   └─ Python package dependencies (install with: pip install -r requirements.txt)
│
└── FILE_GUIDE.md (this file)
    └─ Navigation and index of all files
```

### Python Scripts & Tools (`LLM/`)
```
LLM/
│
├── captioning_pipeline.py ⭐⭐
│   Purpose: Command-line batch processing of images
│   Usage: python captioning_pipeline.py --input_dir ... --output_dir ...
│   Best for: Large-scale automated caption generation
│
├── captioning_interactive.ipynb ⭐⭐⭐
│   Purpose: Step-by-step interactive workflow
│   Usage: jupyter notebook captioning_interactive.ipynb
│   Best for: Learning, testing, visual feedback
│   Includes: Dataset exploration, caption generation, visualization
│
├── data_explorer.py
│   Purpose: Analyze dataset structure and properties
│   Usage: python data_explorer.py
│   Output: JSON report, image list CSV
│   Best for: Understanding your dataset
│
├── vit.ipynb (existing)
│   Purpose: Vision Transformer experiments
│   Note: Part of original project
│
├── vit_ordered.ipynb (existing)
│   Purpose: Ordered Vision Transformer implementation
│   Note: Part of original project
│
└── vit_simple.py (existing)
    Purpose: Simple Vision Transformer baseline
    Note: Part of original project
```

### Annotations & Output (`annotations/`)
```
annotations/
│
├── CAPTION_VALIDATION_CHECKLIST.md ⭐⭐
│   └─ Quality criteria, phase-specific validation, examples
│
├── DATASET_TEMPLATE.json
│   └─ JSON template for final annotated dataset
│
├── captions.json (generated)
│   └─ Raw captions from LLM
│
├── captions_validated.json (generated)
│   └─ Filtered and validated captions
│
├── annotated_dataset.json (generated)
│   └─ Complete dataset with all metadata
│
├── annotated_dataset.csv (generated)
│   └─ CSV version for Excel/spreadsheets
│
├── quality_metrics.json (generated)
│   └─ Statistical analysis of captions
│
├── validation_report.json (generated)
│   └─ Results of caption validation
│
├── dataset_exploration_report.json (generated)
│   └─ Analysis of dataset structure
│
├── image_list.csv (generated)
│   └─ All images with metadata
│
├── dataset_distribution.png (generated)
│   └─ Bar chart of images per phase
│
└── sample_images_with_captions.png (generated)
    └─ Visual preview of sample images
```

### Dataset Structure (`balanced_crystallization/`)
```
balanced_crystallization/
│
├── phy_sugar_db/
│   ├── unsaturated/      (Images)
│   ├── labile/           (Images)
│   ├── intermediate/     (Images)
│   └── metastable/       (Images)
│
├── phy_sugar_opr/
│   ├── unsaturated/      (Images)
│   ├── labile/           (Images)
│   ├── intermediate/     (Images)
│   └── metastable/       (Images)
│
└── vir_polymer/
    ├── unsaturated/      (Images)
    ├── labile/           (Images)
    ├── intermediate/     (Images)
    └── metastable/       (Images)
```

---

## 📚 Reading Guide by Use Case

### Use Case 1: "I just want to get started quickly"
1. Read: [QUICK_START.md](QUICK_START.md) (5 min)
2. Run: `python LLM/data_explorer.py` (1 min)
3. Open: `LLM/captioning_interactive.ipynb` (30+ min)
4. Follow notebook cells sequentially

### Use Case 2: "I want to understand the project deeply"
1. Read: [README.md](README.md) (10 min)
2. Read: [PROJECT_GUIDE.md](PROJECT_GUIDE.md) (20 min)
3. Study: Phase definitions and examples
4. Review: [CAPTION_VALIDATION_CHECKLIST.md](annotations/CAPTION_VALIDATION_CHECKLIST.md)
5. Explore: Dataset with `data_explorer.py`

### Use Case 3: "I want to generate captions for my data"
1. Organize images by phase in subdirectories
2. Run: `python LLM/data_explorer.py` to analyze
3. Set up API key (see QUICK_START.md)
4. Use: Either `captioning_pipeline.py` or `captioning_interactive.ipynb`
5. Validate: Using `CAPTION_VALIDATION_CHECKLIST.md`
6. Export: As JSON/CSV for training

### Use Case 4: "I want to validate and filter captions"
1. Read: [CAPTION_VALIDATION_CHECKLIST.md](annotations/CAPTION_VALIDATION_CHECKLIST.md)
2. Use: Quality scoring rubric (90-100 = Excellent)
3. Manually review 10-20% of captions
4. Document issues and corrections
5. Regenerate poor captions
6. Create `captions_validated.json`

### Use Case 5: "I want to train a model with the captions"
1. Complete caption generation and validation
2. Load: `annotated_dataset.json`
3. Reference: Integration section in [PROJECT_GUIDE.md](PROJECT_GUIDE.md)
4. Create: PyTorch Dataset class
5. Train: Vision Transformer or other model
6. See: `LLM/vit.ipynb` for examples

---

## 🔑 Key Concepts

### Files by Purpose

#### 📖 Learning/Understanding
| File | Content | Time |
|------|---------|------|
| README.md | Overview & context | 10 min |
| PROJECT_GUIDE.md | Full methodology | 30 min |
| QUICK_START.md | Get started fast | 5 min |
| CAPTION_VALIDATION_CHECKLIST.md | Quality criteria | 15 min |

#### 🛠️ Tools/Scripts
| File | Purpose | Complexity |
|------|---------|-----------|
| data_explorer.py | Dataset analysis | ⭐ Easy |
| captioning_pipeline.py | Batch processing | ⭐⭐ Medium |
| captioning_interactive.ipynb | Step-by-step workflow | ⭐⭐ Medium |

#### 📊 Output/Data
| File | Type | When Generated |
|------|------|----------------|
| captions.json | Raw LLM output | After caption generation |
| annotated_dataset.json | Final dataset | After validation |
| quality_metrics.json | Statistics | Auto-generated |
| image_list.csv | Metadata | From data_explorer.py |

---

## 🚀 Typical Workflow

```
Start Here (Pick One)
  ↓
┌─────────────────────────────────────┐
│ QUICK_START.md (5 min)              │
│ for: Just want to run it            │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ PROJECT_GUIDE.md (30 min)           │
│ for: Understanding everything       │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Step 1: Explore Dataset             │
│ Run: python LLM/data_explorer.py    │
│ Generates: report.json, image_list  │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Step 2: Configure LLM               │
│ Set API key (see QUICK_START.md)    │
│ Choose: OpenAI or Anthropic         │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Step 3: Generate Captions           │
│ Method A: Jupyter notebook (learn)  │
│ Method B: CLI script (automate)     │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Step 4: Validate Quality            │
│ Use: CAPTION_VALIDATION_CHECKLIST   │
│ Generates: captions_validated.json  │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Step 5: Use for Training            │
│ Load: annotated_dataset.json        │
│ Train: Vision Transformer models    │
└─────────────────────────────────────┘
```

---

## 💡 Tips & Recommendations

### Before Running Scripts
- [ ] Read QUICK_START.md first
- [ ] Test with small sample (5-10 images)
- [ ] Monitor API costs carefully
- [ ] Keep API keys in environment variables
- [ ] Have annotations/ directory created

### During Execution
- [ ] Start with `data_explorer.py` to understand data
- [ ] Use Jupyter notebook first time for learning
- [ ] Test with single image before full batch
- [ ] Monitor API rate limits
- [ ] Save progress frequently

### After Caption Generation
- [ ] Review samples manually
- [ ] Check quality_metrics.json
- [ ] Use CAPTION_VALIDATION_CHECKLIST.md
- [ ] Validate at least 10% of captions
- [ ] Fix obvious errors
- [ ] Save validated version

---

## ❓ Quick Answers

**Q: Where do I start?**
A: Read QUICK_START.md, then run data_explorer.py

**Q: How do I generate captions?**
A: Use either captioning_interactive.ipynb (learn) or captioning_pipeline.py (automate)

**Q: What's the output?**
A: JSON files with captions, CSV for Excel, PNG visualizations, quality metrics

**Q: How do I validate captions?**
A: Use CAPTION_VALIDATION_CHECKLIST.md and quality_score in JSON

**Q: How do I use captions for training?**
A: Load annotated_dataset.json, create PyTorch Dataset, see PROJECT_GUIDE.md

**Q: What if I encounter errors?**
A: See QUICK_START.md troubleshooting section

**Q: How much does it cost?**
A: ~$0.02-0.10 per image with LLM APIs (see QUICK_START.md)

---

## 🔗 Internal Links

### Main Documentation
- [README.md](README.md) - Project overview
- [PROJECT_GUIDE.md](PROJECT_GUIDE.md) - Detailed methodology
- [QUICK_START.md](QUICK_START.md) - Setup & execution

### Tools & Scripts
- [LLM/captioning_interactive.ipynb](LLM/captioning_interactive.ipynb) - Interactive workflow
- [LLM/captioning_pipeline.py](LLM/captioning_pipeline.py) - Automated pipeline
- [LLM/data_explorer.py](LLM/data_explorer.py) - Dataset analysis

### Validation & Reference
- [annotations/CAPTION_VALIDATION_CHECKLIST.md](annotations/CAPTION_VALIDATION_CHECKLIST.md) - Quality criteria
- [annotations/DATASET_TEMPLATE.json](annotations/DATASET_TEMPLATE.json) - Output structure

---

## 📈 Project Phases

### Phase 1: Planning & Setup ✓
- Understand crystallization phases
- Prepare documentation
- Set up file structure
- Create scripts

### Phase 2: Exploration
- Run data_explorer.py
- Analyze dataset structure
- Understand image properties

### Phase 3: Caption Generation
- Configure LLM API
- Generate captions using notebook or CLI
- Monitor quality and costs

### Phase 4: Validation
- Review captions manually
- Calculate quality scores
- Identify and fix errors

### Phase 5: Finalization
- Create final dataset
- Export JSON/CSV
- Document changes
- Ready for training

### Phase 6: Training (Future)
- Use annotated_dataset.json
- Train Vision Transformer
- Evaluate performance

---

## 📞 Support & Troubleshooting

### Common Issues
- **API Key Error** → See QUICK_START.md section 2
- **Image Not Found** → Check dataset path and structure
- **Rate Limit** → Reduce batch size or wait
- **Poor Captions** → Regenerate with better prompt

### Resources
- QUICK_START.md - Troubleshooting section
- PROJECT_GUIDE.md - Section 6 Next Steps
- CAPTION_VALIDATION_CHECKLIST.md - Issue examples

### Further Help
- Check error messages carefully
- Read full documentation
- Test with sample first
- Review example captions
- Refer to research paper

---

## 📋 Checklist: Using This Guide

- [ ] Read README.md
- [ ] Read QUICK_START.md  
- [ ] Understand the 4 phases
- [ ] Run data_explorer.py
- [ ] Set up API key
- [ ] Generate first batch of captions
- [ ] Review captions against CHECKLIST
- [ ] Validate quality scores
- [ ] Export final dataset
- [ ] Prepare for model training

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-18  
**Status:** Complete & Ready to Use

---

## Navigation Quick Links

🏠 [Home](README.md) • 
🚀 [Quick Start](QUICK_START.md) • 
📖 [Full Guide](PROJECT_GUIDE.md) • 
✅ [Validation](annotations/CAPTION_VALIDATION_CHECKLIST.md) • 
🛠️ [Tools](LLM/) • 
📊 [Template](annotations/DATASET_TEMPLATE.json)
