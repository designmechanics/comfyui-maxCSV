from server import PromptServer
import os
import random
from aiohttp import web
import json
import csv

root_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.abspath(os.path.join(root_dir, "../csv"))

class Max_CSV_Loader_Dynamic:
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

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("output_1", "output_2", "output_3", "output_4", "output_5", "output_6", "output_7", "output_8", "TOTAL_ROWS", "PROMPT")
    FUNCTION = "browse_csv"
    CATEGORY = "Max NODES"
    DESCRIPTION = "Loads rows from a CSV file with dynamic outputs."

    def browse_csv(self, csv_file, selection_type="single", selected_row="", filter_text="", iteration_index=0, extra_pnginfo=None):
        if iteration_index is None:
            iteration_index = 0

        global csv_path
        csv_file_path = os.path.join(csv_path, csv_file)
        csv_file_path = os.path.abspath(csv_file_path)

        if not os.path.isfile(csv_file_path):
            return ("", "", "", "", "", "", "", "", 0, "")

        try:
            with open(csv_file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = [h.strip() for h in next(reader)]
                rows = list(reader)
        except Exception as e:
            return ("", "", "", "", "", "", "", "", 0, "")

        if filter_text:
            rows = [row for row in rows if any(filter_text.lower() in str(cell).lower() for cell in row)]

        total_rows = len(rows)

        if not rows:
            return ("", "", "", "", "", "", "", "", total_rows, "")

        selected_indices = []
        if selection_type == "random":
            selected_indices = [random.randint(0, len(rows) - 1)]
        elif selection_type == "multiple":
            if selected_row:
                try:
                    selected_indices = [int(idx) for idx in selected_row.split(",") if idx.strip().isdigit() and int(idx) < len(rows)]
                except Exception:
                    selected_indices = []
        elif selection_type == "iterate":
            current_iteration_index = iteration_index
            if extra_pnginfo and 'workflow' in extra_pnginfo and 'extra' in extra_pnginfo['workflow']:
                batch_index = extra_pnginfo['workflow']['extra'].get('batch_index', 0)
                current_iteration_index += batch_index
            safe_index = current_iteration_index % len(rows)
            selected_indices = [safe_index]
        else:  # single
            if not selected_row or not selected_row.isdigit() or int(selected_row) >= len(rows):
                selected_indices = [0]
            else:
                selected_indices = [int(selected_row)]

        if not selected_indices:
            selected_indices = [0]

        # Get the first selected row
        first_row = rows[selected_indices[0]]

        # Create the output tuple
        outputs = [first_row[i] if i < len(first_row) else "" for i in range(8)]

        # Get the prompt output
        prompt_output = ""
        try:
            lower_headers = [h.lower() for h in headers]
            if 'prompt' in lower_headers:
                prompt_col_idx = lower_headers.index('prompt')
                if prompt_col_idx < len(first_row):
                    prompt_output = first_row[prompt_col_idx]
        except Exception as e:
            prompt_output = ""

        # Create the return names tuple
        return_names = [f"{headers[i]}" if i < len(headers) else "" for i in range(8)]

        return {"ui": {"string_table": [headers] + rows, "selected_row": selected_row}, "result": tuple(outputs + [total_rows, prompt_output])}

    @classmethod
    def IS_CHANGED(cls, selection_type, csv_file, selected_row="", filter_text="", iteration_index=0):
        if selection_type == "random" or selection_type == "iterate":
            return float('nan')
        return f"{csv_file}:{selection_type}:{selected_row}:{filter_text}:{iteration_index}"

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

@PromptServer.instance.routes.get("/max_csv_browser/get_rows")
async def get_rows(request):
    csv_file = request.query.get("csv_file", "")
    if not csv_file:
        return web.json_response({"error": "csv_file not specified"}, status=400)

    global csv_path
    csv_file_path = os.path.join(csv_path, csv_file)
    csv_file_path = os.path.abspath(csv_file_path)

    if not os.path.isfile(csv_file_path):
        return web.json_response({"error": "File not found"}, status=404)

    try:
        with open(csv_file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = [h.strip() for h in next(reader)]
            rows = list(reader)
            return web.json_response({"headers": headers, "rows": rows})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
