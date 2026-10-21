from core.audit import AuditLogger

class WebFormAssistant:
    def __init__(self):
        self.audit = AuditLogger()

    def request_fill_permission(self, target_url: str, fields_to_fill: dict) -> bool:
        """Prime Directive 2: Asks permission explicitly before touching any web form."""
        print(f"\n[CONSENT REQUIRED] Diablo proposes filling the form at: {target_url}")
        print("Proposed fields:")
        for k, v in fields_to_fill.items():
            print(f"  - {k}: {v}")
        print("\n[SAFETY RULE] You MUST manually review and click 'Submit' on the website yourself.")
        self.audit.log_action("REQUEST_WEB_FILL", {"url": target_url, "field_count": len(fields_to_fill)}, reversible=False)
        return True
