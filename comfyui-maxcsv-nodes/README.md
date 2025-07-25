# MaxCSV Nodes for ComfyUI

> **Easy-to-use, Advanced Features** - A comprehensive node pack for ComfyUI that provides dynamic file browsing, text processing, and data management capabilities.

[![Install](https://img.shields.io/badge/Install-Instructions-blue)](#installation) [![Nodes](https://img.shields.io/badge/Nodes-Documentation-green)](#nodes) [![Example](https://img.shields.io/badge/Example-Workflows-orange)](#example)

---

## Table of Contents

| [Installation](#installation) | [Nodes](#nodes) | [Example](#example) |
|:---:|:---:|:---:|
| Setup guide and requirements | Complete node documentation | Workflow examples and usage |

---

## Installation

### Prerequisites
- **ComfyUI** - Latest version recommended
- **Python 3.x** - Python 3.8 or higher
- **Dependencies** - Automatically installed via requirements.txt

### Quick Setup

1. **Clone the repository** to your ComfyUI custom_nodes directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/designmechanics/comfyui-maxcsv-nodes.git
   ```

2. **Install dependencies**:
   ```bash
   cd comfyui-maxcsv-nodes
   pip install -r requirements.txt
   ```

3. **Restart ComfyUI**

4. **Verify installation** - Look for "Max NODES" category in the node browser

### Manual Installation
If you prefer manual installation:
```bash
pip install aiohttp Pillow
```

### File Structure Setup
Create the following directories in the project root (if they don't exist):
```
comfyui-maxcsv-nodes/
├── PROMPTS/          # For prompt text files
├── CSV/             # For CSV data files  
└── TAGS/            # For tag files
```

---

## Nodes

### File Loader Nodes
File loader nodes allows visual and intuitive selection of prompts, tags or other texts via custom UI.
All loader nodes can output single or multiple texts based on selection, as well as randomize selection or batch all texts.
All loader nodes can read files form subdirectories.

#### **Max Prompt Loader**
Loads full content of text files based on selection. Supports image thumbnails.
Locate "PROMPTS" folder in "../custom_nodes/comfyui-maxcsv-nodes" to add personalized prompts.
Thumnails are shown if there is an image (.png/.jpg) file with the name matching the .txt file name in the same folder

#### **Max CSV Loader**
Loads and processes content of CSV files based on rows.
The node can now extract `prompt` and `filename` values from the CSV file if the corresponding columns are present.
Locate "CSV" folder in "../custom_nodes/comfyui-maxcsv-nodes" to add personalized csv files.

#### **Max Tag Loader**
Loads whole lines of text based on selection.
Locate "TAGS" folder in "../custom_nodes/comfyui-maxcsv-nodes" to add personalized tag sets.

### Text Processing Nodes

#### **Max Extract Prompt**
Utility node, expected to be used with File loaders.
Extracts content from text based on headers. Can extract all non-header content or specific section.

#### **Max Find & Replace**
Performs find and replace operations on text strings with case-sensitive replacement.

#### **Max Text Concatenate**
Combines any number of text inputs with customizable delimiters and text beautification options.

#### **Max Input**
Simple text input node for manual text entry with universal output type.

#### **Max Text to Size**
Extracts width and height values from text strings containing size information.

---

## Example Workflow

*This section is reserved for workflow examples and usage notes.*

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**designmechanics**

</div>
