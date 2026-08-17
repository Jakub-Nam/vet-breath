from app.models.enums import Recommendation
from app.services.rule_engine import evaluate


def test_low_bpm_returns_recount():
    assert evaluate(10) == Recommendation.recount
    assert evaluate(30) == Recommendation.recount


def test_mid_bpm_returns_check():
    assert evaluate(31) == Recommendation.check_membranes_hr
    assert evaluate(40) == Recommendation.check_membranes_hr


def test_high_bpm_returns_go_to_vet():
    assert evaluate(41) == Recommendation.go_to_vet
    assert evaluate(100) == Recommendation.go_to_vet


def test_boundary_30_is_recount():
    assert evaluate(30) == Recommendation.recount


def test_boundary_31_is_check():
    assert evaluate(31) == Recommendation.check_membranes_hr


def test_boundary_40_is_check():
    assert evaluate(40) == Recommendation.check_membranes_hr


def test_boundary_41_is_go_to_vet():
    assert evaluate(41) == Recommendation.go_to_vet
