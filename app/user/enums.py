from enum import Enum

ROLE_OPTIONS = (
    ("Admin", "Admin"),
    ("Initiator", "Initiator"),
    ("Verifier", "Verifier"),
    ("Approver", "Approver"),
)

GENDER_OPTION = (
    ("Male", "Male"),
    ("Female", "Female"),
)

TOKEN_TYPE = (
    ("CreateToken", "CreateToken"),
    ("ResetToken", "ResetToken"),
)


class PinEnum(Enum):
    Transaction = "Transaction"
    Transfer = "Transfer"
