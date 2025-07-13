from server import PromptServer  # type: ignore // ComfyUI Core
import os
import random
from aiohttp import web
import json

root_dir = os.path.dirname(os.path.abspath(__file__))
tags_path = os.path.abspath(os.path.join(root_dir, "../tags"))

class EZ_Tag_Loader:
    @classmethod
    def INPUT_TYPES(cls):
        global tags_path
        try:
            txt_files = []
            for root, dirs, files in os.walk(tags_path):
                for f in files:
                    if f.lower().endswith('.txt'):
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, tags_path)
                        txt_files.append(rel_path)
        except Exception as e:
            txt_files = []

        return {
            "required": {
                "tags_file": (txt_files,),
                "selection_type": (["single", "multiple", "random"], {"default": "single"}),
            },
            "optional": {
                "filter_text": ("STRING", {"default": ""}),
                "selected_tags": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("STRING", "OPT_FILEPATH", "BATCH_SELECTED")
    OUTPUT_IS_LIST = (False, False, True)

    FUNCTION = "browse_tags"

    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Loads tags from a text file based on UI selection
Each line in the text file is considered a separate tag
Selection types:
- single: Select one tag at a time
- multiple: Select multiple tags (comma-separated)
- random: Randomly select one tag on each prompt queue
"""

    def browse_tags(self, tags_file, selection_type="single", selected_tags="", filter_text=""):
        global tags_path
        tags_file = os.path.join(tags_path, tags_file)
        tags_file = os.path.abspath(tags_file)

        if not os.path.isfile(tags_file):
            return ("No tags file found", tags_file, [])

        # Read tags from file
        with open(tags_file, "r", encoding="utf-8") as f:
            tags = [line.strip() for line in f.readlines() if line.strip()]

        if not tags:
            return ("No tags found in file", tags_file, [])

        # Filter tags if filter_text is provided
        if filter_text:
            tags = [tag for tag in tags if filter_text.lower() in tag.lower()]

        if not tags:
            return ("No matching tags found", tags_file, [])

        # Handle different selection types
        selected_list = []
        if selection_type == "random":
            if selected_tags:
                selected_tags_list = [tag.strip() for tag in selected_tags.split(",")]
                valid_selected_tags = [tag for tag in selected_tags_list if tag in tags]
                if valid_selected_tags:
                    selected = random.choice(valid_selected_tags)
                else:
                    selected = random.choice(tags)
            else:
                selected = random.choice(tags)
            selected_list = [selected]
        elif selection_type == "multiple":
            if selected_tags:
                selected_list = [tag.strip() for tag in selected_tags.split(",") if tag.strip() in tags]
        else:  # single
            if not selected_tags or selected_tags not in tags:
                selected_list = [tags[0]]
            else:
                selected_list = [selected_tags]

        # Main output
        main_output = ", ".join(selected_list)

        # List output: if 0 or 1 selected, output all tags; else output selected_list
        if len(selected_list) <= 1:
            all_output = tags
        else:
            all_output = selected_list

        return (main_output, tags_file, all_output)

    @classmethod
    def IS_CHANGED(cls, selection_type, tags_file, selected_tags="", filter_text=""):
        if selection_type == "random":
            return float('nan')
        return selected_tags + str(tags_file) + str(selection_type)

    @classmethod
    def VALIDATE_INPUTS(cls, tags_file, selected_tags=""):
        global tags_path
        tags_file = os.path.join(tags_path, tags_file)
        tags_file = os.path.abspath(tags_file)
        if not os.path.isfile(tags_file):
            return "Tags file does not exist"
        return True

def get_directory_structure(path):
    structure = {"name": os.path.basename(path), "children": [], "path": path, "expanded": False}
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    structure["children"].append(get_directory_structure(entry.path))
    except PermissionError:
        pass
    return structure

def get_tags_from_file(file_path, filter_text=""):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tags = [line.strip() for line in f.readlines() if line.strip()]
            
            # Apply filter if provided
            if filter_text:
                filter_text = filter_text.lower()
                tags = [tag for tag in tags if filter_text in tag.lower()]
                
            return tags
    except Exception as e:
        print(f"Error reading tags file {file_path}: {e}")
        return []

@PromptServer.instance.routes.post("/ez_tag_browser/get_directory_structure")
async def api_get_directory_structure(request):
    try:
        data = await request.json()
        path = data.get("path", "./")
        filter_text = data.get("filter", "")

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return web.json_response({"error": "Path does not exist"}, status=400)

        # If path is a file, get its directory
        if os.path.isfile(path):
            directory = os.path.dirname(path)
            structure = get_directory_structure(directory)
            tags = get_tags_from_file(path, filter_text)
        else:
            structure = get_directory_structure(path)
            tags = []

        response_data = {
            "structure": structure,
            "tags": tags
        }
        
        return web.json_response(response_data)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@PromptServer.instance.routes.post("/ez_tag_browser/get_file_info")
async def get_file_info(request):
    try:
        data = await request.json()
        rel_path = data.get("relative_path", "")
        
        full_path = os.path.normpath(os.path.join(tags_path, rel_path))
        if not full_path.startswith(tags_path):
            return web.json_response({"error": "Invalid path"}, status=400)

        if not os.path.exists(full_path):
            return web.json_response({"error": "File not found"}, status=404)

        return web.json_response({
            "full_path": full_path,
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)