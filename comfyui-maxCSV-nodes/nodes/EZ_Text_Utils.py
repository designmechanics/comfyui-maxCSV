import re
import os
from server import PromptServer  # type: ignore # - server is a part of ComfyUI Core
from aiohttp import web

def clean_text(text):
    text = re.sub(r'\n','####', text) # Replace line breaks to keep it for future (line breaks should not be deleted by default
    text = re.sub(r'\s+,', ',', text) # Remove spaces before commas
    text = re.sub(r',+', ',', text) # Remove duplicate commas
    text = re.sub(r',(\S)', r', \1', text) # Add a space after a comma if it's followed by a word without space
    text = re.sub(r'[ \t]+', ' ', text) # Replace multiple spaces with a single space, while keeping newlines
    text = re.sub(r'\.,|,\.', '.', text) # Replace incorrect combinations like '.,' and ',.' with '.'
    text = re.sub(r"####",'\n', text) # Return line breaks
    text = re.sub(r'(\n\s*){3,}', '\n\n', text) # Consolidate three or more consecutive newlines into two
    text = text.strip().replace(" .", ".") # Remove spaces before periods
    text = re.sub(r',(\S)', r' ', text) # Add a space after a comma if it's followed by a word without space
    cleaned_lines = [line.lstrip("., ") for line in text.splitlines()] # Delete excess commas
    text = "\n".join(cleaned_lines)
    return text

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class EZ_Input:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "String": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = (any, )
    RETURN_NAMES = ("any", )
    FUNCTION = "to_string"
    CATEGORY = "EZ NODES"

    def to_string(self, String):
        
        Combo = String
        return (Combo, )

class EZ_Extract_Prompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "searchword": ("STRING", {"multiline": False, "default": ""}),
                "extract_all": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_prompt"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Extracts full lines of text from input text based on the header provided in input

If "extract_all" is set ot true, node will return the original text with all headers removed

Use with EZ_CSV_Loader to extract text content based on header name
"""

    def extract_prompt(self, string, searchword, extract_all):
        if extract_all:
            result = []
            for line in string.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue  # Skip empty lines
                if stripped.endswith(":") and len(stripped.split()) == 1:
                    continue  # Skip headers
                result.append(line)
            return ("\n".join(result),)

        searchword = searchword.lower()
        collect = False
        lines_out = []

        for line in string.splitlines():
            if not collect:
                # Detect header line
                header = line.strip()
                if header.lower().rstrip(':') == searchword:
                    collect = True
                continue

            # Stop on first empty line
            if line.strip() == "":
                break
            lines_out.append(line)

        return ("\n".join(lines_out),)
        
class EZ_Find_Replace:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
            "optional": {
                "find": ("STRING", {"multiline": False, "default": ""}),
                "replace": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "find_replace"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Finds and replaces all instances of text string
"""

    def find_replace(self, string, find, replace):
        string = string.replace(find, replace)
        return (string,)

class EZ_Text_Concat: # inspired by WAS-Suite by Jordan Thompson (WASasquatch) and Bjornulf nodes

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number_of_inputs": ("INT", {"default": 2, "min": 2, "max": 50, "step": 1}),
                "delimiter": ("STRING", {"default": "\\n"}),
                "beautify": (["never", "before", "after"], {"default": "never"}),
                "line_breaks": (["keep", "delete"], {"default": "keep"}),
            },
            "hidden": {
                **{f"text_{i}": ("STRING", {"forceInput": "True"}) for i in range(1, 51)}
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "text_concatenate"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Concatenate any number of string inputs into a single string with options to beatify text before or after concatenation

use single or multiple "\\n" inputs as delimiter to add line breaks
"""

    def text_concatenate(self, delimiter, beautify, line_breaks, number_of_inputs, **kwargs):
        text_inputs = [] 
        delimiter=delimiter.replace("\\n","\n")
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            if isinstance(v, str):
                if beautify == "before":
                        v=clean_text(v)
                if v != "":
                    text_inputs.append(v)
        merged_text = delimiter.join(text_inputs)
        print(merged_text)
        if beautify == "after":
            merged_text = clean_text(merged_text)
        if line_breaks == "delete":
            merged_text = re.sub(r'\n',' ', merged_text)
            merged_text = re.sub(r'\s+', ' ', merged_text)
        return (merged_text,)
    
class EZ_Text_to_Size:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "1024x1024"}),
            },
        }

    RETURN_TYPES = (any, any,)
    RETURN_NAMES = ("WIDTH", "HEIGHT",)
    FUNCTION = "extract_size"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Extract numbers from text string to be used as width and height
"""

    def extract_size(self, text):
        # Extract all numbers from the text using regex
        numbers = re.findall(r'\d+', text)
        
        # Return last two numbers as width and height
        width = int(numbers[-2])
        height = int(numbers[-1])
        
        return (width, height,)

    @classmethod
    def VALIDATE_INPUTS(cls, text):
        # Extract all numbers from the text using regex
        numbers = re.findall(r'\d+', text)
        
        # Check if we have at least 2 numbers
        if len(numbers) < 2:
            return "Need at least 2 numbers in text"
        return True
        