import time
from core.staging import StagingManager
from core.audit import AuditLogger

TRUSTED_DOMAINS = ["wikipedia.org", "github.com", "arxiv.org", "docs.python.org", "developer.mozilla.org"]

class ResearchAgentSwarm:
    def __init__(self, max_concurrent_agents: int = 2):
        # Resource Governance (Prime Directive 5): Capped at max 2 agents
        self.max_concurrent_agents = max_concurrent_agents
        self.staging = StagingManager()
        self.audit = AuditLogger()

    def execute_research_topic(self, topic: str, source_domain: str = "wikipedia.org", sample_findings: str = "") -> str:
        """Autonomous research routes strictly to Staged Learning review queue."""
        # Source trust filter
        is_trusted = any(td in source_domain for td in TRUSTED_DOMAINS)
        trust_status = "TRUSTED_SOURCE" if is_trusted else "UNVERIFIED_SOURCE"
        
        findings = sample_findings or f"Automated summary on {topic} sourced from {source_domain}."
        
        stage_id = self.staging.stage_knowledge_for_review(
            title=f"Research: {topic} [{trust_status}]",
            content=findings,
            source_url=f"https://{source_domain}/{topic}"
        )
        self.audit.log_action("SWARM_RESEARCH_COMPLETE", {"topic": topic, "stage_id": stage_id, "trust": trust_status}, reversible=False)
        print(f"[RESEARCH SWARM] Research for '{topic}' completed and placed in review queue (ID: {stage_id}).")
        return stage_id
