import json
import collections

def final_merge():
    target_file = 'whmx/logic_models/core/status_library_v3.json'
    batch_files = [
        'whmx/logic_models/archive/rebuild_batch_1.json',
        'whmx/logic_models/archive/rebuild_batch_2.json',
        'whmx/logic_models/archive/rebuild_batch_3.json',
        'whmx/logic_models/archive/rebuild_batch_4.json',
        'whmx/logic_models/archive/rebuild_batch_5.json',
        'whmx/logic_models/archive/rebuild_batch_6.json',
        'whmx/logic_models/archive/rebuild_omissions.json'
    ]

    all_logic = collections.OrderedDict()

    for f_path in batch_files:
        try:
            with open(f_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                all_logic.update(data.get('STATUS_LOGIC', {}))
        except Exception as e:
            print(f"Error reading {f_path}: {e}")

    # 补录元数据中未包含但逻辑引用的核心基础状态
    supplementary = {
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
    
    all_logic.update(supplementary)

    final_data = {
        "version": "3.1.0",
        "description": "物华弥新器者状态逻辑库 - 语义回溯恢复终极版",
        "STATUS_LOGIC": all_logic
    }

    try:
        with open(target_file, 'w', encoding='utf-8-sig') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"✅ SUCCESS: Consolidated {len(all_logic)} statuses into {target_file}")
    except Exception as e:
        print(f"❌ FAILED to write target file: {e}")

if __name__ == "__main__":
    final_merge()
