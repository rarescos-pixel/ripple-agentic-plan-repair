from __future__ import annotations
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List
from ripple.domain.models import PlanNode, NodeKind, DependencyEdge, ChangeEvent, Impact, ImpactStatus
from ripple.tools.simulated import ToolRegistry


class DependencyEngine:
    def __init__(self, nodes: Dict[str, PlanNode], edges: List[DependencyEdge], tools: ToolRegistry):
        self.nodes = nodes
        self.edges = edges
        self.tools = tools
        self.outgoing = defaultdict(list)
        for edge in edges:
            self.outgoing[edge.upstream_id].append(edge)

    @staticmethod
    def _dt(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def _condition_met(self, edge: DependencyEdge, node: PlanNode, change: ChangeEvent) -> bool:
        if edge.condition == "always":
            return True
        new_value = self._dt(change.new_value if isinstance(change.new_value, str) else None)
        if new_value is None:
            return False
        if edge.condition == "arrival_after_start":
            start = self._dt(node.start_at)
            return start is not None and new_value > start
        if edge.condition == "arrival_after_end":
            end = self._dt(node.end_at)
            return end is not None and new_value > end
        raise ValueError(f"Unknown dependency condition: {edge.condition}")

    def detect_impacts(self, change: ChangeEvent) -> List[Impact]:
        impacts: List[Impact] = []
        q = deque([(change.node_id, [change.node_id])])
        seen = {change.node_id}
        while q:
            current, path = q.popleft()
            for edge in self.outgoing.get(current, []):
                if edge.downstream_id in seen:
                    continue
                seen.add(edge.downstream_id)
                node = self.nodes[edge.downstream_id]
                if not self._condition_met(edge, node, change):
                    continue
                options = self.tools.repair_options(node)
                # Facts may be intermediate dependency nodes. Actionable nodes
                # remain visible as impacts even when no safe repair exists.
                if options or node.kind != NodeKind.FACT:
                    impacts.append(Impact(
                        affected_node_id=node.id,
                        dependency_path=path + [node.id],
                        reason=(
                            f"{node.title} violates dependency after the changed fact"
                            if options else
                            f"{node.title} is affected but has no safe repair option"
                        ),
                        status=ImpactStatus.AT_RISK if options else ImpactStatus.INVALID,
                        direct_cash_at_risk=node.financial_exposure,
                        urgency=int(node.attributes.get("urgency", 50)),
                        options=options,
                    ))
                q.append((node.id, path + [node.id]))
        return sorted(impacts, key=lambda x: (-x.urgency, x.affected_node_id))
