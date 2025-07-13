from .nodes.EZ_Testing import EZ_Test # TESTING

from .nodes.EZ_Prompt_Loader import EZ_Prompt_Loader
from .nodes.EZ_CSV_Loader import EZ_CSV_Loader
from .nodes.EZ_Tag_Loader import EZ_Tag_Loader
from .nodes.EZ_Text_Utils import \
    EZ_Extract_Prompt, \
    EZ_Text_to_Size, \
    EZ_Find_Replace, \
    EZ_Text_Concat, \
    EZ_Input

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

NODE_CLASS_MAPPINGS = {
    "EZ_Test": EZ_Test, # TESTING

    "EZ_Prompt_Loader": EZ_Prompt_Loader,
    "EZ_CSV_Loader": EZ_CSV_Loader,
    "EZ_Tag_Loader": EZ_Tag_Loader,
    "EZ_Extract_Prompt": EZ_Extract_Prompt,
    "EZ_Find_Replace": EZ_Find_Replace,
    "EZ_Text_Concat": EZ_Text_Concat,
    "EZ_Input": EZ_Input,
    "EZ_Text_to_Size": EZ_Text_to_Size,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EZ_Test": "EZ Test Node", # TESTING

    "EZ_Prompt_Loader": "EZ Prompt Loader",
    "EZ_CSV_Loader": "EZ CSV Loader",
    "EZ_Tag_Loader": "EZ Tag Loader",
    "EZ_Extract_Prompt": "EZ Extract Prompt",
    "EZ_Find_Replace": "EZ Find & Replace",
    "EZ_Text_Concat": "EZ Text Concatenate",
    "EZ_Input": "EZ Input",
    "EZ_Text_to_Size": "EZ Text to Size",
}

WEB_DIRECTORY = "./web"