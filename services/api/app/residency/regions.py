"""Supported data residency regions (NFR-06)."""

from enum import Enum


class DataRegion(str, Enum):
    IN = "IN"
    EU = "EU"
    SG = "SG"


REGION_LABELS: dict[DataRegion, str] = {
    DataRegion.IN: "India",
    DataRegion.EU: "European Union",
    DataRegion.SG: "Singapore (Asia-Pacific)",
}

# Platform routing hints — maps to cloud region identifiers at deploy time
STORAGE_REGION_ENDPOINTS: dict[DataRegion, str] = {
    DataRegion.IN: "ap-south-1",  # AWS Mumbai / Azure Central India
    DataRegion.EU: "eu-west-1",
    DataRegion.SG: "ap-southeast-1",
}

PROCESSING_REGION_ENDPOINTS: dict[DataRegion, str] = {
    DataRegion.IN: "ap-south-1",
    DataRegion.EU: "eu-west-1",
    DataRegion.SG: "ap-southeast-1",
}

TLS_MIN_VERSION = "1.2"
ENCRYPTION_AT_REST = "AES-256"
