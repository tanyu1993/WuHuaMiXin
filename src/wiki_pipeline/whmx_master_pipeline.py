
import os, sys
# 路径配置 - 使用新的项目结构
_WIKI_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_WIKI_PIPELINE_DIR)))
_DATA_ROOT = os.path.join(_PROJECT_ROOT, "data")

if _WIKI_PIPELINE_DIR not in sys.path: sys.path.insert(0, _WIKI_PIPELINE_DIR)
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)
# -*- coding: utf-8 -*-
"""
WuHuaMiXin - Master Automated Pipeline
Version: 3.0 (Industrialized & Unified)
Logic: Step 1 (Global Fetch) -> Step 2 (Precision Clip) -> Step 3 (Logical Refine) -> Step 4 (Aggregate)
"""
import os, sys, subprocess

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_command(cmd):
    try:
        # 在 Windows 环境下，使用 python 而不是 python3
        # 使用当前解释器以确保路径一致性
        subprocess.run(f"{sys.executable} {os.path.join(SCRIPT_DIR, cmd)}", check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Pipeline ERROR] Executing {cmd} failed: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python whmx_master_pipeline.py <CharacterName>  # Process a specific character from Wiki to Hub")
        print("  python whmx_master_pipeline.py --rebuild-all    # Re-run clip, refine, and aggregate for ALL raw files")
        return

    target = sys.argv[1]

    if target == "--rebuild-all":
        print("\n>>> STARTING FULL INDUSTRIALIZED REBUILD PIPELINE <<<")
        print(">>> [Phase 2] Precision Clipping ALL files in raw/...")
        if not run_command("step2_precision_clip.py"): return
        
        print(">>> [Phase 3] Logical Refining (V2.1 Ultra Plus Max)...")
        if not run_command("step3_refine_ultra.py"): return
        
        print(">>> [Phase 4] Updating Intelligence Hub & Search Page...")
        if not run_command("step4_aggregate_hub.py"): return
        
        print(">>> [Phase 5] Syncing Status Metadata (Grouped & Sorted)...")
        if not run_command("step5_sync_status_metadata.py"): return
        
        print(f"\n>>> FULL REBUILD COMPLETE! View: {status_search_path}")
    else:
        print(f"\n>>> [Pipeline 3.0] STARTING AUTOMATED FLOW FOR: {target} <<<")
        
        # 1. Global Fetch (P0-P2 + IP Rotation)
        print(f"\n>>> [Step 1] Initializing Global Fetcher (P0 Priority)...")
        if not run_command(f"step1_fetch_wiki.py {target}"):
            print(f"Pipeline ABORTED: Global fetch failed for {target}.")
            return
        
        # 2. Precision Clip & Burst (Physical Anchor Slicing)
        print(f"\n>>> [Step 2] Applying Precision Clip (Start: ![Name.png] | End: 考核)...")
        # 由于 step2 会自动扫描 raw/ 目录，它可以一并处理新抓取的和其他遗留文件
        if not run_command("step2_precision_clip.py"):
            print(f"Pipeline ABORTED: Step 2 failed for {target}.")
            return
        
        # 3. Logical Refine (V2.1 Ultra Logic)
        print(f"\n>>> [Step 3] Logical Refining (V2.1 Ultra Plus Max)...")
        if not run_command("step3_refine_ultra.py"):
            print(f"Pipeline ABORTED: Step 3 failed for {target}.")
            return
        
        # 4. Hub Aggregation
        print(f"\n>>> [Step 4] Updating Status Intelligence Hub...")
        if not run_command("step4_aggregate_hub.py"):
            print(f"Pipeline ABORTED: Step 4 failed for {target}.")
            return
            
        # 5. Metadata Sync
        print(f"\n>>> [Step 5] Syncing Status Metadata (Grouped & Sorted)...")
        if not run_command("step5_sync_status_metadata.py"):
            print(f"Pipeline ABORTED: Step 5 failed for {target}.")
            return
        
        # Final Success Message
        status_search_path = os.path.join(_PROJECT_ROOT, "data", "status_viewer.html")
        print(f"\n>>> [Pipeline SUCCESS] '{target}' processed from Wiki to Intelligence Hub! <<<")
        print(f">>> View results in: {status_search_path}")

if __name__ == "__main__":
    main()
