import json
import os

def fix_batch_01():
    chars_path = r'whmx\logic_models\characters'
    files = [f for f in os.listdir(chars_path) if f.endswith('.json')]
    
    for f in files:
        path = os.path.join(chars_path, f)
        with open(path, 'r', encoding='utf-8-sig') as j:
            data = json.load(j)
        
        modified = False
        
        # Recursive fixer
        def visit(node):
            nonlocal modified
            if isinstance(node, dict):
                # Fix: TELEPORT_TO_ALLY_RADIUS -> TELEPORT
                if node.get('type') == 'TELEPORT_TO_ALLY_RADIUS':
                    node['type'] = 'TELEPORT'
                    node['target_type'] = 'ALLY_RADIUS'
                    modified = True
                
                # Fix: AOE_SPLASH -> DEAL_DAMAGE + range
                if node.get('type') == 'AOE_SPLASH':
                    node['type'] = 'DEAL_DAMAGE'
                    node['is_splash'] = True
                    modified = True

                for k, v in node.items():
                    visit(v)
            elif isinstance(node, list):
                for item in node:
                    visit(item)

        visit(data)
        
        if modified:
            print(f"🔧 Fixing {f}...")
            with open(path, 'w', encoding='utf-8-sig') as j:
                json.dump(data, j, ensure_ascii=False, indent=2)
        else:
            print(f"✨ {f} is clean.")

if __name__ == "__main__":
    fix_batch_01()
