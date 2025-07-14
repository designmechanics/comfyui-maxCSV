from server import PromptServer  # type: ignore // ComfyUI Core
import os
import random
from aiohttp import web
import json
import csv

root_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.abspath(os.path.join(root_dir, "../csv"))

class Max_CSV_Loader_Dynamic:
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("output_1", "output_2", "output_3", "output_4", "output_5", "output_6", "output_7", "output_8", "TOTAL_ROWS")

    def __init__(self):
        self.selected_csv = None

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

    @classmethod
    def IS_CHANGED(cls, selection_type, csv_file, selected_row="", filter_text="", iteration_index=0):
        if selection_type == "random" or selection_type == "iterate":
            return float('nan')

        if iteration_index is None:
            iteration_index = 0
        return f"{csv_file}:{selection_type}:{selected_row}:{filter_text}:{iteration_index}"

    def browse_csv(self, csv_file, selection_type="single", selected_row="", filter_text="", iteration_index=0, extra_pnginfo=None):
        # Gracefully handle the case where the optional input is not connected
        if iteration_index is None:
            iteration_index = 0

        global csv_path
        csv_file_path = os.path.join(csv_path, csv_file)
        csv_file_path = os.path.abspath(csv_file_path)

        if not os.path.isfile(csv_file_path):
            return ("", "", "", "", "", "", "", "", 0)

        try:
            with open(csv_file_path, "r", encoding="utf-8-sig") as f:
                first_line = f.readline()
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(first_line, delimiters=",;")
                except Exception:
                    dialect = csv.excel
                reader = list(csv.reader(f, dialect))
                if not reader or len(reader) < 2:
                    return ("", "", "", "", "", "", "", "", 0)
                headers = [h.strip() for h in reader[0]]
                rows = reader[1:]

                rows = [row for row in rows if any(cell and cell.strip() for cell in row)]
        except Exception as e:
             return ("", "", "", "", "", "", "", "", 0)

        if filter_text:
            rows = [row for row in rows if any(filter_text.lower() in str(cell).lower() for cell in row)]

        total_rows = len(rows)

        if not rows:
            return ("", "", "", "", "", "", "", "", total_rows)

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
            # Create a dictionary from the row using headers as keys
            row_dict = {header: (row[i] if i < len(row) else "") for i, header in enumerate(headers)}

            # Extract values for each output name in RETURN_NAMES
            output_row = [row_dict.get(name, "") for name in self.RETURN_NAMES[:-1]]
            outputs.append(output_row)

        # For simplicity, we'll just use the first selected row for output
        final_outputs = outputs[0] if outputs else [""] * 8
        final_outputs.append(total_rows)

        # Update RETURN_NAMES to include the header names
        new_return_names = []
        for i, header in enumerate(headers):
            new_return_names.append(f"output_{i+1} ({header})")

        # Add the remaining output names
        for i in range(len(headers), 8):
            new_return_names.append(f"output_{i+1}")

        new_return_names.append("TOTAL_ROWS")
        self.RETURN_NAMES = tuple(new_return_names)

        return tuple(final_outputs)

    FUNCTION = "browse_csv"
    CATEGORY = "Max NODES"
    DESCRIPTION = """
Loads rows from a CSV file based on UI selection, with dynamic outputs based on the CSV header.
Each row in the CSV is selectable; the first row is used as headers
Selection types:
- single: Select one row at a time
- multiple: Select multiple rows (comma-separated indices)
- random: Randomly select one row on each prompt queue
- iterate: Select a single row by its index number. Increments for each item in a batch.
"""

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

@PromptServer.instance.routes.post("/max_csv_browser/get_directory_structure")
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

@PromptServer.instance.routes.post("/max_csv_browser/get_file_info")
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
