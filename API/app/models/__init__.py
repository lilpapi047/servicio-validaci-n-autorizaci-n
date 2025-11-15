from .models import (
    User,
    Match,
    RaffleAssignment,
    AttendanceBan,
    EmailVerification,
    EligibilityCriterion,
    EligibilityAudit,
)

# Alias so code that expects `models.Ban` keeps working
Ban = AttendanceBan

__all__ = [
    "User",
    "Match",
    "RaffleAssignment",
    "AttendanceBan",
    "EmailVerification",
    "EligibilityCriterion",
    "EligibilityAudit",
    "Ban",
]
