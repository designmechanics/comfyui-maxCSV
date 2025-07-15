from server import PromptServer  # type: ignore // ComfyUI Core
import os
import random
from aiohttp import web
import json
import csv

root_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.abspath(os.path.join(root_dir, "../csv"))

class EZ_CSV_Loader:
    @classmethod
    def INPUT_TYPES(cls):
        global csv_path
        try:
            csv_files = []
            for root, dirs, files in os.walk(csv_path):
                for f in files:
                    if f.lower().endswith('.csv'):
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, csv_path)
                        csv_files.append(rel_path)
        except Exception as e:
            csv_files = []

        return {
            "required": {
                "csv_file": (csv_files,),
                "selection_type": (["single", "multiple", "random", "iterate"], {"default": "single"}),
            },
            "optional": {
                "filter_text": ("STRING", {"default": ""}),
                "selected_row": ("STRING", {"default": ""}),
                "iteration_index": ("INT", {"default": 0, "min": 0, "max": 999999, "step": 1}),
            }
        }

    RETURN_TYPES = ("STRING", "OPT_FILEPATH", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("STRING", "OPT_FILEPATH", "BATCH_SELECTED", "PROMPT", "FILENAME", "TOTAL_ROWS")
    OUTPUT_IS_LIST = (False, False, True, False, False, False)

    FUNCTION = "browse_csv"

    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Loads rows from a CSV file based on UI selection
Each row in the CSV is selectable; the first row is used as headers
Selection types:
- single: Select one row at a time
- multiple: Select multiple rows (comma-separated indices)
- random: Randomly select one row on each prompt queue
- iterate: Select a single row by its index number. Increments for each item in a batch.
"""

    def browse_csv(self, csv_file, selection_type="single", selected_row="", filter_text="", iteration_index=0, extra_pnginfo=None):
        """
        Loads data from a CSV. In 'iterate' mode, it uses the extra_pnginfo 
        provided by ComfyUI to handle batch processing correctly.
        """
        # Gracefully handle the case where the optional input is not connected
        if iteration_index is None:
            iteration_index = 0

        global csv_path
        csv_file = os.path.join(csv_path, csv_file)
        csv_file = os.path.abspath(csv_file)

        if not os.path.isfile(csv_file):
            return ("No CSV file found", csv_file, [], "", "", 0)

        try:
            with open(csv_file, "r", encoding="utf-8-sig") as f:
                first_line = f.readline()
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(first_line, delimiters=",;")
                except Exception:
                    dialect = csv.excel
                reader = list(csv.reader(f, dialect))
                if not reader or len(reader) < 2:
                    return ("No data rows found in file", csv_file, [], "", "", 0)
                headers = [h.strip() for h in reader[0]]
                rows = reader[1:]
                
                rows = [row for row in rows if any(cell and cell.strip() for cell in row)]
        except Exception as e:
             return (f"Error reading CSV: {e}", csv_file, [], "", "", 0)

        if filter_text:
            rows = [row for row in rows if any(filter_text.lower() in str(cell).lower() for cell in row)]
        
        total_rows = len(rows)

        if not rows:
            return ("No matching rows found", csv_file, [], "", "", total_rows)

        selected_indices = []
        if selection_type == "random":
            selected_indices = [random.randint(0, len(rows)-1)]
        elif selection_type == "multiple":
            if selected_row:
                try:
                    selected_indices = [int(idx) for idx in selected_row.split(",") if idx.strip().isdigit() and int(idx) < len(rows)]
                except Exception:
                    selected_indices = []
        elif selection_type == "iterate":
            # --- BATCH PROCESSING LOGIC ---
            # Get the starting index from the UI
            current_iteration_index = iteration_index
            
            # If we are in a batch, ComfyUI provides extra_pnginfo
            if extra_pnginfo and 'workflow' in extra_pnginfo and 'extra' in extra_pnginfo['workflow']:
                # Get the batch index, which starts at 0 for the first run
                batch_index = extra_pnginfo['workflow']['extra'].get('batch_index', 0)
                current_iteration_index += batch_index
            
            # Use modulo to wrap around if the index exceeds the number of rows
            safe_index = current_iteration_index % len(rows)
            selected_indices = [safe_index]
        else:  # single
            if not selected_row or not selected_row.isdigit() or int(selected_row) >= len(rows):
                selected_indices = [0]
            else:
                selected_indices = [int(selected_row)]
        
        if not selected_indices:
             selected_indices = [0]

        outputs = []
        for idx in selected_indices:
            row = rows[idx]
            out = ""
            for i, h in enumerate(headers):
                v = row[i] if i < len(row) else ""
                out += f"{h}:\n\n{v}\n\n"
            outputs.append(out.strip())
        output_str = "\n---\n".join(outputs)

        filename_output = ""
        try:
            lower_headers = [h.lower() for h in headers]
            if 'filename' in lower_headers:
                filename_col_idx = lower_headers.index('filename')
                first_selected_idx = selected_indices[0]
                first_row = rows[first_selected_idx]
                if filename_col_idx < len(first_row):
                    filename_output = first_row[filename_col_idx]
        except Exception as e:
            print(f"EZ_CSV_Loader: Could not extract filename. Error: {e}")
            filename_output = ""

        prompt_output = ""
        try:
            lower_headers = [h.lower() for h in headers]
            if 'prompt' in lower_headers:
                prompt_col_idx = lower_headers.index('prompt')
                first_selected_idx = selected_indices[0]
                first_row = rows[first_selected_idx]
                if prompt_col_idx < len(first_row):
                    prompt_output = first_row[prompt_col_idx]
        except Exception as e:
            print(f"EZ_CSV_Loader: Could not extract prompt. Error: {e}")
            prompt_output = ""

        if selection_type == "iterate" or selection_type == "single":
            all_indices = list(range(len(rows)))
        elif selection_type == "multiple":
            all_indices = selected_indices if selected_indices else []
        else: # random
            all_indices = selected_indices

        all_outputs = []
        for idx in all_indices:
            row = rows[idx]
            out = ""
            for i, h in enumerate(headers):
                v = row[i] if i < len(row) else ""
                out += f"{h}:\n\n{v}\n\n"
            all_outputs.append(out.strip())

        return (output_str, csv_file, all_outputs, prompt_output, filename_output, total_rows)

    @classmethod
    def IS_CHANGED(cls, selection_type, csv_file, selected_row="", filter_text="", iteration_index=0):
        # For 'random' and 'iterate', we want the node to execute for every run in a batch.
        # Returning float('nan') tells ComfyUI that the output is always different.
        if selection_type == "random" or selection_type == "iterate":
            return float('nan')
            
        if iteration_index is None:
            iteration_index = 0
        return f"{csv_file}:{selection_type}:{selected_row}:{filter_text}:{iteration_index}"

    # The VALIDATE_INPUTS function has been removed to prevent the pre-execution crash.
    # The node's main browse_csv function will handle file existence checks.

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

def get_rows_from_csv(file_path, filter_text=""):
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            first_line = f.readline()
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(first_line, delimiters=",;")
            except Exception:
                dialect = csv.excel
            reader = list(csv.reader(f, dialect))
            if not reader or len(reader) < 2:
                return {"headers": [], "rows": []}
            headers = reader[0]
            rows = reader[1:]
            
            rows = [row for row in rows if any(cell and cell.strip() for cell in row)]
            
            if filter_text:
                rows = [row for row in rows if any(filter_text.lower() in str(cell).lower() for cell in row)]
            return {"headers": headers, "rows": rows}
    except Exception as e:
        print(f"Error reading CSV file {file_path}: {e}")
        return {"headers": [], "rows": []}

@PromptServer.instance.routes.post("/ez_csv_browser/get_directory_structure")
async def api_get_directory_structure(request):
    try:
        data = await request.json()
        path = data.get("path", "./")
        filter_text = data.get("filter", "")

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return web.json_response({"error": "Path does not exist"}, status=400)

        if os.path.isfile(path):
            directory = os.path.dirname(path)
            structure = get_directory_structure(directory)
            csv_data = get_rows_from_csv(path, filter_text)
        else:
            structure = get_directory_structure(path)
            csv_data = {"headers": [], "rows": []}

        response_data = {
            "structure": structure,
            "headers": csv_data["headers"],
            "rows": csv_data["rows"]
        }
        return web.json_response(response_data)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@PromptServer.instance.routes.post("/ez_csv_browser/get_file_info")
async def get_file_info(request):
    try:
        data = await request.json()
        rel_path = data.get("relative_path", "")
        full_path = os.path.normpath(os.path.join(csv_path, rel_path))
        if not full_path.startswith(os.path.abspath(csv_path)):
            return web.json_response({"error": "Invalid path"}, status=400)
        if not os.path.exists(full_path):
            return web.json_response({"error": "File not found"}, status=404)
        return web.json_response({
            "full_path": full_path,
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
