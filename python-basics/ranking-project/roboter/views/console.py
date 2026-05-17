import os
import string

def get_template(template_file):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_file_path = os.path.join(base_dir, "templates", template_file)
    with open(template_file_path, "r", encoding="utf-8") as f:
        template = string.Template(f.read())
    return template
