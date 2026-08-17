from app.models.enums import Recommendation

BPM_RECOUNT_UPPER = 30
BPM_CHECK_UPPER = 40


def evaluate(bpm: int) -> Recommendation:
    if bpm <= BPM_RECOUNT_UPPER:
        return Recommendation.recount
    if bpm <= BPM_CHECK_UPPER:
        return Recommendation.check_membranes_hr
    return Recommendation.go_to_vet
