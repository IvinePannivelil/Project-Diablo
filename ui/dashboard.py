from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from core.governance import ResourceGovernor
from core.staging import StagingManager
from core.audit import AuditLogger

app = FastAPI(title="Diablo Central Command")
governor = ResourceGovernor()
staging = StagingManager()
audit = AuditLogger()

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    headroom = governor.check_system_headroom()
    pending = staging.get_pending_queue()
    recent_logs = audit.get_recent_actions(limit=5)
    
    status_html = '<span class="halt-badge">EMERGENCY HALT ACTIVE</span>' if headroom['emergency_halted'] else '<span class="status-badge">ONLINE - SAFE MODE</span>'
    heavy_task_str = 'YES' if headroom['can_load_heavy_task'] else 'BLOCKED'
    
    pending_items_html = ''
    if pending:
        for i in pending:
            name = i.get('title') or i.get('source_path') or 'Item'
            pending_items_html += f"<li><strong>[{i['type']}]</strong> {name} (Status: {i['status']})</li>"
    else:
        pending_items_html = '<p style="color: #9ca3af;">Review queue clean. No unverified actions pending.</p>'
        
    logs_html = ''
    for l in recent_logs:
        logs_html += f"<li>[{l['readable_time']}] <strong>{l['action_type']}</strong> - {l['details']}</li>"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Diablo Control Center</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0b0f19; color: #f3f4f6; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .header {{ display: flex; align-items: center; justify-content: space-between; }}
        .title {{ font-size: 24px; font-weight: bold; color: #ef4444; }}
        .avatar-hud {{ text-align: center; padding: 20px; background: #030712; border-radius: 8px; border: 1px dashed #374151; }}
        .avatar-face {{ font-size: 48px; }}
        .status-badge {{ background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; }}
        .halt-badge {{ background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; }}
        .metric {{ font-size: 16px; margin: 8px 0; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ background: #1f2937; padding: 10px; border-radius: 6px; margin-bottom: 8px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card header">
            <div>
                <div class="title">PROJECT DIABLO</div>
                <div style="color: #9ca3af; font-size: 14px;">Privacy-First Local AI Assistant (RTX 4060)</div>
            </div>
            <div>
                {status_html}
            </div>
        </div>

        <div class="card avatar-hud">
            <div class="avatar-face">[ - _ - ]</div>
            <div style="margin-top: 10px; color: #9ca3af;">2D Reactive HUD Interface | Profile: <strong>{governor.current_profile}</strong></div>
        </div>

        <div class="card">
            <h3>Resource Governance (Prime Directive 5)</h3>
            <div class="metric">System RAM Used: <strong>{headroom['ram_used_percent']}%</strong> (Limit: {headroom['ram_limit_percent']}%)</div>
            <div class="metric">CPU Activity: <strong>{headroom['cpu_percent']}%</strong></div>
            <div class="metric">Heavy Task Headroom: <strong>{heavy_task_str}</strong></div>
        </div>

        <div class="card">
            <h3>Staged Learning Queue (Prime Directive 4)</h3>
            <ul>{pending_items_html}</ul>
        </div>

        <div class="card">
            <h3>Audit Trail and Reversibility (Prime Directive 6)</h3>
            <ul>{logs_html}</ul>
        </div>
    </div>
</body>
</html>"""
    return html