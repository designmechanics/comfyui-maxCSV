import os

root_dir = os.path.dirname(os.path.abspath(__file__))
prompts_path = os.path.abspath(os.path.join(root_dir, "../prompts"))

class EZ_Test:
    @classmethod
    def INPUT_TYPES(cls):

        global prompts_path
        try:
            prompt_dirs = []
            for root, dirs, files in os.walk(prompts_path):
                for d in dirs:
                    full_path = os.path.join(root, d)
                    rel_path = os.path.relpath(full_path, prompts_path)
                    prompt_dirs.append(rel_path)
        except Exception:
            prompt_dirs = []

        return {
            "required": {
                "prompt_directory": (prompt_dirs,)
            },
            # "optional": {
            #     "selected_file": ("STRING", {"default": ""}),
            # }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "doit"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
TEST NODE 
"""

    def doit(self, prompt_directory):
        global root_dir
        prompt_directory = os.path.join(root_dir, prompt_directory)
        return (prompt_directory,)