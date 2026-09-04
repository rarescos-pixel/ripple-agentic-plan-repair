from __future__ import annotations
import hashlib
from typing import Dict
from ripple.domain.models import ChangeEvent, RepairAction, RepairPlan, PlanNode
from ripple.engine.dependency import DependencyEngine


class Planner:
    def __init__(self, nodes: Dict[str, PlanNode], engine: DependencyEngine):
        self.nodes = nodes
        self.engine = engine

    def _allowed_options(self, impact):
        node = self.nodes[impact.affected_node_id]
        disallowed = set(node.attributes.get("disallowed_operations", []))
        return [o for o in impact.options if o.operation not in disallowed]

    def build_plan(self, change: ChangeEvent) -> RepairPlan:
        impacts = self.engine.detect_impacts(change)
        actions = []
        unresolved = []
        for impact in impacts:
            options = self._allowed_options(impact)
            if not options:
                unresolved.append(impact.affected_node_id)
                continue
            option = min(options, key=lambda o: (o.added_cost, -o.avoidable_loss, o.operation))
            key_material = f"{change.id}|{impact.affected_node_id}|{option.tool}|{option.operation}|{option.params}"
            idem = hashlib.sha256(key_material.encode()).hexdigest()[:24]
            actions.append(RepairAction(
                id=f"action:{len(actions)+1}", tool=option.tool, operation=option.operation,
                target_id=impact.affected_node_id, params=option.params,
                reversible=option.reversible, external_side_effect=option.external_side_effect,
                added_cost=option.added_cost, avoidable_loss=option.avoidable_loss,
                idempotency_key=idem,
            ))
        total_added = sum(a.added_cost for a in actions)
        total_avoidable = sum(a.avoidable_loss for a in actions)
        external_people = sum(self.nodes[a.target_id].external_people for a in actions if a.tool == "calendar")
        return RepairPlan(
            id=f"plan:{change.id}", version=1, source_change_event_id=change.id,
            impacts=impacts, actions=actions, total_added_cost=total_added,
            total_avoidable_loss=total_avoidable, external_people_notified=external_people,
            unresolved_items=unresolved,
        )
