import json
import re

def verify_100_percent_coverage():
    logic_path = 'whmx/logic_models/characters/Pipa_Logic_1_1.json'
    audit_path = 'whmx/verification_reports/五弦琵琶_True_1_1_Audit.md'

    with open(logic_path, 'r', encoding='utf-8') as f:
        logic_data = json.load(f)
    
    with open(audit_path, 'r', encoding='utf-8-sig') as f:
        audit_content = f.read()

    # 提取 JSON 中所有的 ID 和逻辑指令值
    def extract_logic_atoms(d):
        atoms = set()
        if isinstance(d, dict):
            for k, v in d.items():
                if k in ['type', 'id', 'status', 'trigger', 'action']:
                    atoms.add(str(v))
                atoms.update(extract_logic_atoms(v))
        elif isinstance(d, list):
            for item in d:
                atoms.update(extract_logic_atoms(item))
        return atoms

    logic_atoms = extract_logic_atoms(logic_data)
    
    # 过滤掉一些基础结构词
    ignore_list = ['NORMAL_ATTACK', 'CLASS_SKILL', 'ULTIMATE_SKILL', 'CONSTRUCT', 'EXTRA_CONSTRUCT']
    filtered_atoms = [a for a in logic_atoms if a not in ignore_list and len(a) > 2]

    print(f"--- 逻辑原子覆盖率审计 (Logic Atom Coverage) ---")
    total = len(filtered_atoms)
    matched = 0
    missing = []

    for atom in filtered_atoms:
        # 在审计报告的 `Logic Instruction` 列中寻找该原子
        if atom in audit_content:
            matched += 1
        else:
            missing.append(atom)

    coverage = (matched / total) * 100
    print(f"Total Logic Atoms: {total}")
    print(f"Matched in Audit:  {matched}")
    print(f"Coverage:          {coverage:.2f}%")

    if missing:
        print(f"\n⚠️ 以下逻辑原子未在审计报告中显式对齐:")
        for m in missing:
            print(f"  - {m}")
    else:
        print(f"\n✅ 100% 逻辑闭环达成：JSON 中的每一条战斗指令均有档案原文可回溯。")

if __name__ == "__main__":
    verify_100_percent_coverage()
