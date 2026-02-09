import re
import os

def parse_conf(conf_path):
    settings = {}
    if not os.path.exists(conf_path):
        return settings
    with open(conf_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('CONFIG_') and '=' in line:
                key, val = line.split('=')
                settings[key.strip()] = val.strip().strip('"')
    return settings

def parse_keymap(keymap_path):
    layers = []
    if not os.path.exists(keymap_path):
        return layers
    
    with open(keymap_path, 'r') as f:
        content = f.read()
    
    # Extract only the keymap block
    keymap_match = re.search(r'keymap\s*{(.*)}', content, re.DOTALL)
    if not keymap_match:
        return layers
    keymap_content = keymap_match.group(1)
    
    # Find layers within the keymap block
    layer_pattern = re.compile(r'(\w+)\s*{\s*bindings\s*=\s*<(.*?)>;\s*};', re.DOTALL)
    matches = layer_pattern.findall(keymap_content)
    
    for name, bindings_str in matches:
        # Clean up bindings: remove newlines, multiple spaces, and leading/trailing spaces
        clean_bindings = bindings_str.replace('\n', ' ').strip()
        # Split by space, but handle the fact that some bindings have spaces (though rare in ZMK typical &kp)
        # We look for '&' to identify starts of bindings
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

def format_layer(layer):
    b = layer['bindings']
    # Corne is 42 keys. If it's 36, we handle that too.
    count = len(b)
    
    res = f"### {layer['name'].replace('_', ' ').capitalize()}\n\n"
    
    if count == 42:
        res += "| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |\n"
        res += "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        res += "| **Top** | " + " | ".join(b[0:12]) + " |\n"
        res += "| **Mid** | " + " | ".join(b[12:24]) + " |\n"
        res += "| **Bot** | " + " | ".join(b[24:36]) + " |\n"
        res += "| **Thumb** | | | | " + " | ".join(b[36:39]) + " | " + " | ".join(b[39:42]) + " | | | |\n"
    elif count == 36:
        res += "| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |\n"
        res += "|---|---|---|---|---|---|---|---|---|---|---|\n"
        res += "| **Top** | " + " | ".join(b[0:6]) + " | " + " | ".join(b[6:12]) + " |\n"
        res += "| **Mid** | " + " | ".join(b[12:18]) + " | " + " | ".join(b[18:24]) + " |\n"
        res += "| **Bot** | " + " | ".join(b[24:30]) + " | " + " | ".join(b[30:36]) + " |\n"
    else:
        res += "*Raw bindings (Layout unknown for " + str(count) + " keys):*\n`" + " ".join(b) + "`\n"
    
    res += "\n"
    return res

def generate_readme():
    conf = parse_conf('config/corne.conf')
    layers = parse_keymap('config/corne.keymap')
    
    readme = "# Corne Keyboard ZMK Configuration\n\n"
    readme += "Automatic documentation generated on every push.\n\n"
    
    readme += "## 🛠 Current Settings\n\n"
    important_keys = [
        'CONFIG_ZMK_KEYBOARD_NAME',
        'CONFIG_ZMK_DISPLAY',
        'CONFIG_ZMK_STUDIO',
        'CONFIG_ZMK_SLEEP',
        'CONFIG_BT_CTLR_TX_PWR_PLUS_8'
    ]
    
    readme += "| Setting | Value |\n|---|---|\n"
    for k in important_keys:
        if k in conf:
            readme += f"| {k.replace('CONFIG_ZMK_', '').replace('CONFIG_', '').replace('_', ' ')} | `{conf[k]}` |\n"
    readme += "\n"
    
    readme += "## 📖 Usage Guide\n\n"
    readme += "### Pairing\n"
    readme += "- Use `BT_SEL 0/1/2` to switch profiles.\n"
    readme += "- Use `BT_CLR` to clear current profile.\n\n"
    readme += "### Features\n"
    if conf.get('CONFIG_ZMK_STUDIO') == 'y':
        readme += "- **ZMK Studio**: Supported. Connect via USB to use the web editor.\n"
    if conf.get('CONFIG_ZMK_DISPLAY') == 'y':
        readme += "- **OLED Display**: Enabled with battery, layer, and WPM status.\n"
    readme += "\n"
    
    readme += "## ⌨️ Layout Configuration\n\n"
    for layer in layers:
        readme += format_layer(layer)
    
    with open('README.md', 'w') as f:
        f.write(readme)

if __name__ == "__main__":
    generate_readme()
