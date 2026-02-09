import re
import os

def parse_keymap(keymap_path):
    layers = []
    if not os.path.exists(keymap_path):
        return layers
    
    with open(keymap_path, 'r') as f:
        content = f.read()
    
    keymap_match = re.search(r'keymap\s*{(.*)}', content, re.DOTALL)
    if not keymap_match:
        return layers
    keymap_content = keymap_match.group(1)
    
    layer_pattern = re.compile(r'(\w+)\s*{\s*bindings\s*=\s*<(.*?)>;\s*};', re.DOTALL)
    matches = layer_pattern.findall(keymap_content)
    
    for name, bindings_str in matches:
        clean_bindings = bindings_str.replace('\n', ' ').strip()
        bindings = []
        parts = clean_bindings.split()
        current_binding = ""
        for p in parts:
            if p.startswith('&'):
                if current_binding:
                    bindings.append(current_binding.strip())
                current_binding = p
            else:
                current_binding += " " + p
        if current_binding:
            bindings.append(current_binding.strip())
            
        layers.append({'name': name, 'bindings': bindings})
    
    return layers

def clean_label(label):
    # Strip &kp, &mo, etc. for cleaner ASCII art
    l = re.sub(r'^&kp\s+', '', label)
    l = re.sub(r'^&mo\s+', 'L', l)
    l = re.sub(r'^&ltq\s+\d+\s+', '', l)
    l = re.sub(r'^&td0', 'TD0', l)
    l = re.sub(r'^&trans', '---', l)
    l = re.sub(r'^&bt\s+', '', l)
    return l[:7] # Max 7 chars for alignment

def format_layer_ascii(layer):
    b = [clean_label(x) for x in layer['bindings']]
    if len(b) < 42:
        return f"### {layer['name']}\n(Keymap format not recognized)\n"

    # Row structure helper
    def pad(s): return s.center(7)

    res = f"### {layer['name'].replace('_', ' ').capitalize()}\n"
    res += "```text\n"
    res += "      Left Hand                                     Right Hand\n"
    res += "  " + "_"*47 + "    " + "_"*47 + "\n"
    
    # Row 1
    res += "  | " + " | ".join([pad(b[i]) for i in range(0, 6)]) + " |    | " + " | ".join([pad(b[i]) for i in range(6, 12)]) + " |\n"
    # Row 2
    res += "  | " + " | ".join([pad(b[i]) for i in range(12, 18)]) + " |    | " + " | ".join([pad(b[i]) for i in range(18, 24)]) + " |\n"
    # Row 3
    res += "  | " + " | ".join([pad(b[i]) for i in range(24, 30)]) + " |    | " + " | ".join([pad(b[i]) for i in range(30, 36)]) + " |\n"
    
    # Thumb row
    res += "  " + " "*21 + "| " + " | ".join([pad(b[i]) for i in range(36, 39)]) + " |    | " + " | ".join([pad(b[i]) for i in range(39, 42)]) + " |\n"
    res += "  " + " "*21 + "¯"*23 + "    " + "¯"*23 + "\n"
    
    res += "```\n\n"
    return res

def generate_readme():
    layers = parse_keymap('config/corne.keymap')
    
    readme = "# My Corne Keyboard Layout\n\n"
    readme += "Personal ZMK configuration for the Corne (CRKBD). This documentation is updated automatically on every push.\n\n"
    
    readme += "## ⌨️ Layouts\n\n"
    for layer in layers:
        readme += format_layer_ascii(layer)
    
    with open('README.md', 'w') as f:
        f.write(readme)

if __name__ == "__main__":
    generate_readme()
