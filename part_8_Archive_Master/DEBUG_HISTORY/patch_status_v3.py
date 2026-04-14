import json

def patch_missing_statuses():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    missing = {
        "峰石": {
            "type": "STACK_ACCUMULATOR",
            "description": "千里江山图基础叠加状态",
            "max_stacks": 3
        },
        "流纹": {
            "type": "STACK_ACCUMULATOR",
            "description": "千里江山图基础叠加状态",
            "max_stacks": 3
        },
        "分秒不差": {
            "type": "DYNAMIC_MODIFIER",
            "description": "曾侯乙编钟联动增益",
            "changes": {
                "ATTRIBUTE_REGISTRY.BASE.ATK": 0.15
            },
            "duration": 2
        },
        "黄金比例": {
            "type": "STACK_ACCUMULATOR",
            "description": "断臂维纳斯核心叠加状态",
            "max_stacks": 5
        }
    }

    data['STATUS_LOGIC'].update(missing)

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Patching complete.")

if __name__ == "__main__":
    patch_missing_statuses()
