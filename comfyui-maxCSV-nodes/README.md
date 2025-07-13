# EZ-AF Nodes for ComfyUI

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
   git clone https://github.com/your-repo/comfyui-ez-af-nodes.git
   ```

2. **Install dependencies**:
   ```bash
   cd comfyui-ez-af-nodes
   pip install -r requirements.txt
   ```

3. **Restart ComfyUI**

4. **Verify installation** - Look for "EZ NODES" category in the node browser

### Manual Installation
If you prefer manual installation:
```bash
pip install aiohttp Pillow
```

### File Structure Setup
Create the following directories in the project root (if they don't exist):
```
comfyui-ez-af-nodes/
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

#### **EZ Prompt Loader**
Loads full content of text files based on selection. Supports image thumbnails.
Locate "PROMPTS" folder in "../custom_nodes/comfyui-ez-af-nodes" to add personalized prompts.
Thumnails are shown if there is an image (.png/.jpg) file with the name matching the .txt file name in the same folder

#### **EZ CSV Loader**
Loads and processes content of CSV files based on rows.
Locate "CSV" folder in "../custom_nodes/comfyui-ez-af-nodes" to add personalized csv files.

#### **EZ Tag Loader**
Loads whole lines of text based on selection.
Locate "TAGS" folder in "../custom_nodes/comfyui-ez-af-nodes" to add personalized tag sets.

### Text Processing Nodes

#### **EZ Extract Prompt**
Utility node, expected to be used with File loaders.
Extracts content from text based on headers. Can extract all non-header content or specific section.

#### **EZ Find & Replace**
Performs find and replace operations on text strings with case-sensitive replacement.

#### **EZ Text Concatenate**
Combines any number of text inputs with customizable delimiters and text beautification options.

#### **EZ Input**
Simple text input node for manual text entry with universal output type.

#### **EZ Text to Size**
Extracts width and height values from text strings containing size information.

---

## Example Workflow

*This section is reserved for workflow examples and usage notes.*

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**EZ-AF**

</div>
