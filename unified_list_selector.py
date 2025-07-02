# unified_list_selector.py

import os
import csv
import server
from aiohttp import web

PromptServer = server.PromptServer

def get_lines_from_file(file_path):
    if not file_path or not os.path.isfile(file_path):
        return []
    lines = []
    try:
        with open(file_path, 'r', encoding="utf-8", errors='ignore') as f:
            if file_path.lower().endswith(".csv"):
                reader = csv.reader(f)
                lines = [", ".join(row) for row in reader if any(field.strip() for field in row)]
            else:
                lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[UnifiedListSelector] Erreur de lecture du fichier {file_path}: {e}")
    return lines

@PromptServer.instance.routes.post("/get_list_from_file")
async def get_list_handler(request):
    data = await request.json()
    file_path = data.get("file_path")
    if not file_path:
        return web.Response(status=400, text="Chemin du fichier manquant")
    lines = get_lines_from_file(file_path)
    return web.json_response(lines)

class UnifiedListSelector:
    NODE_NAME = "UnifiedListSelector"
    CATEGORY = "Custom/Tools"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list_file": ("STRING", {"multiline": False, "default": ""}),
                "mode": (["select", "random"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "add_prefix": ("BOOLEAN", {"default": False, "label_on": "Préfixe activé", "label_off": "Préfixe désactivé"}),
                "custom_prefix": ("STRING", {"multiline": True, "default": ""}),
                "add_suffix": ("BOOLEAN", {"default": False, "label_on": "Suffixe activé", "label_off": "Suffixe désactivé"}),
                "custom_suffix": ("STRING", {"multiline": True, "default": ""}),
                "selected_line": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_text",)
    FUNCTION = "execute"

    def execute(self, list_file, mode, seed, 
                add_prefix=False, custom_prefix="", add_suffix=False, custom_suffix="", selected_line=""):

        lines = get_lines_from_file(list_file)
        if not lines:
            return ("",)

        if mode == "random":
            import random
            random.seed(seed)
            base_selection = random.choice(lines)
        elif selected_line in lines:
            base_selection = selected_line
        else:
            base_selection = lines[0]

        final_text = ""
        if add_prefix:
            final_text += custom_prefix
        final_text += base_selection
        if add_suffix:
            final_text += custom_suffix

        return (final_text,)

NODE_CLASS_MAPPINGS = {"UnifiedListSelector": UnifiedListSelector}
NODE_DISPLAY_NAME_MAPPINGS = {"UnifiedListSelector": "Unified List Selector"}
