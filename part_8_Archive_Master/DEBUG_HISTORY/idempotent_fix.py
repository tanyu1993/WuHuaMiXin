import json
import re

def final_idempotent_fix():
    file_path = 'whmx/logic_models/core/status_library_v3.json'
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    # 语义修正映射 (基准值)
    correct_geo = {
        "云峰奇险": "GEOMETRY.RADIUS.SQUARE_3",
        "不负三光": "GEOMETRY.SCOPE.RANDOM_ENEMIES_2",
        "危险食盒": "GEOMETRY.RADIUS.SQUARE_1",
        "同赏": "GEOMETRY.RADIUS.SQUARE_1",
        "壑川": "GEOMETRY.RADIUS.SQUARE_2",
        "将义": "GEOMETRY.RADIUS.SQUARE_10",
        "庆功酒": "GEOMETRY.RADIUS.SQUARE_2",
        "打卡": "GEOMETRY.RADIUS.SQUARE_2",
        "散音": "GEOMETRY.RADIUS.SQUARE_3",
        "残烛回光": "GEOMETRY.RADIUS.SQUARE_4",
        "滔滔": "GEOMETRY.RADIUS.SQUARE_2",
        "素纱": "GEOMETRY.RADIUS.SQUARE_1",
        "经变": "GEOMETRY.RADIUS.SQUARE_1",
        "耀阳永辉": "GEOMETRY.RADIUS.SQUARE_2",
        "莲台": "GEOMETRY.RADIUS.SQUARE_2",
        "落照": "GEOMETRY.RADIUS.SQUARE_1",
        "辑录": "GEOMETRY.RADIUS.SQUARE_2",
        "钟表校准": "GEOMETRY.RADIUS.SQUARE_3",
        "锋镝清野": "GEOMETRY.RADIUS.SQUARE_1",
        "飞雪域": "GEOMETRY.RADIUS.SQUARE_3"
    }

    def clean_geo(text):
        if not isinstance(text, str): return text
        # 1. 先把所有带数字堆叠的几何路径全部抹除，重置为占位符
        text = re.sub(r'GEOMETRY\.(RADIUS|SCOPE)\.SQUARE_[0-9]+', 'REPLACE_ME_GEO', text)
        text = re.sub(r'GEOMETRY\.(RADIUS|SCOPE)\.RANDOM_ENEMIES_[0-9]+', 'REPLACE_ME_GEO', text)
        return text

    def apply_correct_geo(obj, status_name):
        if isinstance(obj, dict):
            return {k: apply_correct_geo(v, status_name) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [apply_correct_geo(i, status_name) for i in obj]
        elif isinstance(obj, str):
            if "REPLACE_ME_GEO" in obj:
                base_name = status_name.split('-')[0]
                replacement = correct_geo.get(base_name, "GEOMETRY.RADIUS.SQUARE_2")
                return obj.replace("REPLACE_ME_GEO", replacement)
            return obj
        return obj

    # 第一步：物理清洗
    data['STATUS_LOGIC'] = {k: clean_geo(v) for k, v in data['STATUS_LOGIC'].items()}
    # 第二步：精确回填
    data['STATUS_LOGIC'] = {k: apply_correct_geo(v, k) for k, v in data['STATUS_LOGIC'].items()}

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Idempotent Logic Reconstruction Complete.")

if __name__ == "__main__":
    final_idempotent_fix()
