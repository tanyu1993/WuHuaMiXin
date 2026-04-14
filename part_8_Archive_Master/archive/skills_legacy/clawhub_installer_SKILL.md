# ClawHub Installer Skill (Gemini CLI Optimized)

## Description
A robust installer for ClawHub skills that uses browser-sniffing and smart-extraction. It bypasses 404/API rate limits by finding direct download links.

## Capability
- **Sniff**: Use `agent-browser` to find `download?slug=xxx` links on ClawHub.
- **Fetch**: Download ZIP files using `curl_cffi` or `Invoke-WebRequest`.
- **Install**: Extract ZIPs, auto-strip version numbers, and handle nested folders.
- **Configure**: Auto-run `pip install -r requirements.txt` or `npm install` if detected.

## Instructions
1. Navigate to ClawHub URL using `agent-browser`.
2. Extract the direct download link from the page source.
3. Download and extract to target directory.
4. Clean up the folder structure to ensure `SKILL.md` is at the root.
5. Report the new skill's summary.
