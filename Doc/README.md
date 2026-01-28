# Sugar Crystallization Image Captioning Project

## 🎯 Project Goal

Transform the seed crystallization dataset from **non-captioning labels** (simple class names: Unsaturated, Labile, Intermediate, Metastable) into a **richly annotated dataset** with detailed captions explaining each crystallization phase.

**Why?** Captions provide:
- Detailed process descriptions for each phase
- Quantifiable metrics (growth percentages)
- Machine learning training data for vision-caption models
- Better understanding of phase transitions
- Cross-verification with multi-modal LLMs

---

## 📚 Reference

**Research Foundation:**  
*"High-Intensified Resemblance and Statistic-Restructured Alignment in Few-Shot Domain Adaptation for Industrial-Specialized Employment"*
- Published: IEEE Transactions on Consumer Electronics, August 2023
- Authors: Jirayu Petchhan, Shun-Feng Su
- Focus: Few-shot domain adaptation techniques applicable to specialized industrial tasks

**Crystallization Theory:**  
Based on solubility diagrams showing:
1. **Unsaturated Zone**: No crystallization (below equilibrium line)
2. **Labile/Nucleation Zone**: Seed formation begins
3. **Meta-stable Zone**: Controlled crystal growth
4. **Stable Solution**: Equilibrium reached

---

## 🏗️ Project Structure

```
d:\user\CEIPP\
├── PROJECT_GUIDE.md                          # Complete project documentation
├── QUICK_START.md                            # Get started in 3 steps
├── 
├── balanced_crystallization/
│   ├── phy_sugar_db/
│   │   ├── unsaturated/     ✓ Images
│   │   ├── labile/          ✓ Images
│   │   ├── intermediate/    ✓ Images
│   │   └── metastable/      ✓ Images
│   ├── phy_sugar_opr/
│   │   ├── unsaturated/
│   │   ├── labile/
│   │   ├── intermediate/
│   │   └── metastable/
│   └── vir_polymer/
│       ├── unsaturated/
│       ├── labile/
│       ├── intermediate/
│       └── metastable/
│
├── annotations/                              # Output directory
│   ├── CAPTION_VALIDATION_CHECKLIST.md      # Quality criteria
│   ├── captions.json                        # Generated captions (LLM output)
│   ├── captions_validated.json              # Validated captions (filtered)
│   ├── annotated_dataset.json               # Final dataset with captions
│   ├── annotated_dataset.csv                # CSV format for Excel
│   ├── quality_metrics.json                 # Quality statistics
│   ├── validation_report.json               # Validation results
│   ├── dataset_exploration_report.json      # Dataset analysis
│   ├── image_list.csv                       # All image metadata
│   ├── dataset_distribution.png             # Chart of image counts
│   └── sample_images_with_captions.png      # Visual samples
│
└── LLM/                                      # Python scripts & notebooks
    ├── captioning_pipeline.py               # Command-line tool
    ├── captioning_interactive.ipynb         # Interactive notebook
    ├── data_explorer.py                     # Dataset exploration
    ├── vit.ipynb                            # Vision Transformer (existing)
    ├── vit_ordered.ipynb                    # Vision Transformer (existing)
    └── vit_simple.py                        # Vision Transformer (existing)
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install & Configure
```bash
# Navigate to project directory
cd d:\user\CEIPP

# Install dependencies
pip install openai anthropic pillow opencv-python pandas matplotlib

# Set API key (choose one)
$env:OPENAI_API_KEY="your_key_here"           # Windows PowerShell
set OPENAI_API_KEY=your_key_here               # Windows Command Prompt
export OPENAI_API_KEY="your_key_here"          # Linux/Mac
```

### Step 2: Run Exploration
```bash
python LLM/data_explorer.py
```
This will analyze your dataset and save reports to `annotations/`

### Step 3: Generate Captions

**Option A: Interactive (Recommended)**
```bash
cd LLM
jupyter notebook captioning_interactive.ipynb
```

**Option B: Command-line**
```bash
python LLM/captioning_pipeline.py \
  --input_dir balanced_crystallization/phy_sugar_db \
  --output_dir annotations \
  --provider openai
```

---

## 📖 Documentation Files

| File | Purpose | Best For |
|------|---------|----------|
| `PROJECT_GUIDE.md` | Complete methodology & context | Understanding the full project |
| `QUICK_START.md` | Get started fast | Running the pipeline |
| `CAPTION_VALIDATION_CHECKLIST.md` | Quality criteria | Validating captions |
| `captioning_pipeline.py` | Batch processing tool | Large-scale automation |
| `captioning_interactive.ipynb` | Interactive notebook | Step-by-step workflow |
| `data_explorer.py` | Dataset analysis | Understanding your data |

---

## 🔄 Workflow

```
┌─────────────────────────┐
│  1. Explore Dataset     │  Run data_explorer.py to understand structure
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│  2. Configure LLM       │  Set API key, choose provider (OpenAI/Anthropic)
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│  3. Generate Captions   │  Use interactive notebook or pipeline script
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│  4. Validate Quality    │  Use checklist to verify caption accuracy
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│  5. Filter & Refine     │  Remove errors, regenerate poor captions
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│  6. Create Dataset      │  Export JSON/CSV for training
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│  7. Train Models        │  Use captions to train Vision Transformer, etc.
└─────────────────────────┘
```

---

## 📊 Crystallization Phases Explained

### 🔹 UNSATURATED (ไม่อิ่มตัว)
- **Visual:** Clear transparent liquid, no particles
- **Growth:** 0%
- **What's Happening:** Solution is under-saturated, no crystallization yet
- **Next Step:** Heat or add more sugar to reach supersaturation

### 🔹 LABILE (ไม่เสถียร)
- **Visual:** Very tiny crystal seeds barely visible, mostly clear
- **Growth:** 5-15%
- **What's Happening:** Nucleation boundary reached, seeds just forming
- **Next Step:** Continue cooling gently to avoid oversaturation

### 🔹 INTERMEDIATE (ระหว่างลิเบิล)
- **Visual:** Visible crystals growing, increasing cloudiness
- **Growth:** 15-50%
- **What's Happening:** Controlled growth phase, multiple nuclei developing
- **Next Step:** Maintain cooling rate for consistent growth

### 🔹 METASTABLE (เสถียรคงเส้น)
- **Visual:** Large well-formed crystals, fully concentrated solution
- **Growth:** 50-100%
- **What's Happening:** Stable equilibrium, crystallization nearly complete
- **Next Step:** Ready for harvest

---

## 📝 Example Captions

### UNSATURATED Example:
```
UNSATURATED: Clear, transparent sugar solution with no visible crystal particles. 
The liquid is under-saturated and in stable equilibrium. No crystallization has 
occurred. Growth: 0%. Stage: Initial, awaiting supersaturation.
```

### LABILE Example:
```
LABILE: Very small crystal nuclei beginning to form in the super-saturated solution. 
Fine particles are barely visible, indicating the nucleation boundary has been crossed. 
The solution remains mostly clear but shows initial turbidity. 
Growth: ~10%. Stage: Primary nucleation, seed formation initiated.
```

### INTERMEDIATE Example:
```
INTERMEDIATE: Visible crystal growth with multiple nuclei developing. 
The solution is progressively becoming cloudy/turbid as crystals expand. 
Particle size is increasing noticeably, ranging from microscopic to small visible 
crystals. Growth: ~35%. Stage: Active controlled growth, crystals establishing structure.
```

### METASTABLE Example:
```
METASTABLE: Well-developed crystals fully formed and in stable growth phase. 
The solution is significantly saturated with mature crystal formations throughout. 
Color intensity is pronounced, indicating high solute concentration. 
Crystals show defined structure and size distribution. 
Growth: ~85%. Stage: Final equilibration, harvest-ready crystallization.
```

---

## 🛠️ Tools & Technologies

### LLM Providers
- **OpenAI GPT-4 Vision**: ~$0.02-0.05 per image, high quality
- **Anthropic Claude 3 Opus**: ~$0.05-0.10 per image, excellent reasoning
- **Open-source** (LLaVA, BLIP-2): Free, requires GPU

### Python Libraries
- `openai` / `anthropic`: LLM API access
- `pillow` / `opencv-python`: Image processing
- `pandas`: Data management
- `matplotlib`: Visualization
- `json`: Data storage

### Output Formats
- **JSON**: `captions.json`, `annotated_dataset.json` (structured data)
- **CSV**: `annotated_dataset.csv` (Excel-compatible)
- **PNG**: Visualizations and sample images

---

## 💰 Cost Estimation

| Task | Provider | Est. Cost (100 imgs) | Est. Cost (1000 imgs) |
|------|----------|---------------------|----------------------|
| Caption Generation | OpenAI GPT-4 | $2-5 | $20-50 |
| Caption Generation | Anthropic Claude | $5-10 | $50-100 |
| Data Exploration | Data Explorer | Free | Free |
| Validation | Manual Review | Time-dependent | - |

**Money-Saving Tips:**
- Start with 10-20 sample images
- Use cheaper models for testing
- Process in batches to monitor costs
- Cache prompts if provider supports it

---

## ✅ Quality Assurance

### Validation Checklist
Every caption should:
- ✓ Identify the crystallization phase
- ✓ Describe observable features
- ✓ Include growth percentage
- ✓ Reference process stage
- ✓ Use correct technical terminology
- ✓ Be grammatically correct
- ✓ Be 100-300 characters long

See `CAPTION_VALIDATION_CHECKLIST.md` for full criteria.

### Quality Scoring
- **Excellent (90-100%):** Ready to use
- **Good (80-89%):** Minor revisions
- **Acceptable (70-79%):** Should review
- **Poor (<70%):** Regenerate

---

## 🔄 Integration with Training

### Using Captions for Vision Transformer
```python
from torchvision import transforms
from torch.utils.data import Dataset

class CrystallizationDataset(Dataset):
    def __init__(self, json_file, transform=None):
        with open(json_file) as f:
            self.data = json.load(f)
        self.transform = transform
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        image = Image.open(item['image_path'])
        caption = item['caption']
        
        if self.transform:
            image = self.transform(image)
        
        return image, caption, item['phase_label']

# Use in training:
dataset = CrystallizationDataset('annotated_dataset.json')
```

---

## 🐛 Troubleshooting

### "API key not found"
- Verify environment variable is set
- Restart terminal after setting
- Check API key is valid on provider website

### "Image file not found"
- Verify dataset path is correct
- Check images are in phase subdirectories
- Verify image format (JPG, PNG, JPEG)

### "Rate limit exceeded"
- Reduce number of images processed
- Wait 1-2 minutes before retrying
- Check API usage dashboard

### "Poor caption quality"
- Adjust LLM system prompt
- Try different LLM provider
- Manually review and correct
- Regenerate using improved prompt

See `QUICK_START.md` for more troubleshooting tips.

---

## 📚 References & Citations

### Research Papers Referenced
- Petchhan, J., & Su, S. F. (2023). High-Intensified Resemblance and Statistic-Restructured Alignment in Few-Shot Domain Adaptation for Industrial-Specialized Employment. *IEEE Transactions on Consumer Electronics*, 69(3), 353-365.

### Related Concepts
- Few-shot learning and domain adaptation
- Vision transformers and multi-modal learning
- Crystallization kinetics and solubility diagrams
- Image captioning and vision-language models

---

## 📋 Checklist: Before Starting

- [ ] Python 3.8+ installed
- [ ] API key obtained (OpenAI or Anthropic)
- [ ] Dataset extracted and organized
- [ ] Dependencies installed (`pip install -r requirements.txt` if available)
- [ ] Output directory created (`annotations/`)
- [ ] Read `QUICK_START.md`
- [ ] Understood the 4 crystallization phases

---

## 🎓 Learning Resources

### For Understanding Crystallization
- Study the `PROJECT_GUIDE.md` section on phases
- Review the solubility diagram in the reference PDF
- Look at examples in `CAPTION_VALIDATION_CHECKLIST.md`

### For Using the Tools
- See `QUICK_START.md` for 3-step setup
- Run `data_explorer.py` to understand your data
- Try the Jupyter notebook for interactive learning

### For Model Training
- Check `LLM/vit.ipynb` for Vision Transformer examples
- See integration section above
- Experiment with different architectures

---

## 📞 Support & Help

### Common Questions

**Q: Can I use different datasets?**  
A: Yes! The pipeline works with any organized image dataset with subdirectories by class.

**Q: How do I use open-source LLMs locally?**  
A: Modify the scripts to use `transformers` library with LLaVA or BLIP-2.

**Q: Can I combine captions from multiple LLMs?**  
A: Yes! Generate with different providers and create an ensemble.

**Q: What if I run out of API budget?**  
A: Use manual captions, switch to open-source, or regenerate for the most important images only.

---

## 📄 License & Usage

This project is designed for research and educational purposes.

**Use responsibly:**
- Monitor API costs carefully
- Start with small samples before full runs
- Keep API keys secure (use environment variables)
- Cite the reference research paper if publishing

---

## 🚀 Next Steps

1. **Read** `QUICK_START.md` for immediate setup
2. **Explore** your data with `data_explorer.py`
3. **Generate** captions using `captioning_interactive.ipynb`
4. **Validate** using `CAPTION_VALIDATION_CHECKLIST.md`
5. **Train** your models with the annotated dataset

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Crystallization Phases | 4 |
| Subdatasets | 3 (phy_sugar_db, phy_sugar_opr, vir_polymer) |
| Expected Images | 100+ per phase |
| Caption Length | 100-300 characters |
| Supported LLM Providers | 2+ (OpenAI, Anthropic, custom) |
| Output Formats | JSON, CSV, PNG |
| Estimated Processing Time | 30-60 sec per image |

---

**Version:** 1.0  
**Created:** 2025-12-18  
**Status:** Production Ready  
**Last Updated:** 2025-12-18

---

## 📬 Quick Links

- [PROJECT_GUIDE.md](PROJECT_GUIDE.md) - Full documentation
- [QUICK_START.md](QUICK_START.md) - Get started in 3 steps
- [LLM/captioning_interactive.ipynb](LLM/captioning_interactive.ipynb) - Interactive notebook
- [annotations/CAPTION_VALIDATION_CHECKLIST.md](annotations/CAPTION_VALIDATION_CHECKLIST.md) - Quality criteria

**Happy Captioning! 🎉**
