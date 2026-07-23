from pydantic import BaseModel
from typing import List


# -----------------------------
# Version Config
# -----------------------------
class VersionConfig(BaseModel):
    latestVersion: str
    minimumSupportedVersion: str
    softUpdate: bool
    forceUpdate: bool
    playStoreUrl: str
    updateTitle: str
    updateMessage: str


# -----------------------------
# Support Config
# -----------------------------
class SupportConfig(BaseModel):
    name: str
    email: str
    mobile1: str
    mobile2: str
    privacyUrl: str
    tncUrl: str
    playStoreUrl: str
    role: str


# -----------------------------
# Reject Reason
# -----------------------------
class RejectReason(BaseModel):
    id: int
    code: str
    name: str


# -----------------------------
# Booking Rule
# -----------------------------
class BookingRule(BaseModel):
    id: int
    message: str


# -----------------------------
# Config Section
# -----------------------------
class ConfigSection(BaseModel):
    version: VersionConfig
    support: SupportConfig


# -----------------------------
# Masters Section
# -----------------------------
class MastersSection(BaseModel):
    rejectReason: List[RejectReason]
    bookingRules: List[BookingRule]


# -----------------------------
# Response Data
# -----------------------------
class ConfigData(BaseModel):
    config: ConfigSection
    masters: MastersSection


# -----------------------------
# API Response
# -----------------------------
class ConfigResponse(BaseModel):
    status: int
    message: str
    errorMessage: str
    data: ConfigData