import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from ripple.golden import run_golden
from ripple.evaluation.rubric import collect_evidence


def test_rubric_evidence_is_quantified():
    plan, first, _, _ = run_golden()
    ev = collect_evidence(plan, first)
    assert any("5 downstream impacts" in x for x in ev.technical_implementation)
    assert any("$116" in x for x in ev.potential_impact)
    assert any("$74" in x for x in ev.potential_impact)
    assert len(ev.quality_of_idea) >= 3
