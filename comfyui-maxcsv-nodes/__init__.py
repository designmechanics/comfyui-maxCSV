from .nodes.MaxTesting import Max_Test # TESTING

from .nodes.MaxPrompt_Loader import Max_Prompt_Loader
from .nodes.MaxCSV_Loader import Max_CSV_Loader
from .nodes.MaxTag_Loader import Max_Tag_Loader
from .nodes.MaxText_Utils import \
    Max_Extract_Prompt, \
    Max_Text_to_Size, \
    Max_Find_Replace, \
    Max_Text_Concat, \
    Max_Input

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

NODE_CLASS_MAPPINGS = {
    "Max_Test": Max_Test, # TESTING

    "Max_Prompt_Loader": Max_Prompt_Loader,
    "Max_CSV_Loader": Max_CSV_Loader,
    "Max_Tag_Loader": Max_Tag_Loader,
    "Max_Extract_Prompt": Max_Extract_Prompt,
    "Max_Find_Replace": Max_Find_Replace,
    "Max_Text_Concat": Max_Text_Concat,
    "Max_Input": Max_Input,
    "Max_Text_to_Size": Max_Text_to_Size,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Max_Test": "Max Test Node", # TESTING

    "Max_Prompt_Loader": "Max Prompt Loader",
    "Max_CSV_Loader": "Max CSV Loader",
    "Max_Tag_Loader": "Max Tag Loader",
    "Max_Extract_Prompt": "Max Extract Prompt",
    "Max_Find_Replace": "Max Find & Replace",
    "Max_Text_Concat": "Max Text Concatenate",
    "Max_Input": "Max Input",
    "Max_Text_to_Size": "Max Text to Size",
}

WEB_DIRECTORY = "./web"