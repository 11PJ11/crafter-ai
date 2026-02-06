"""
DES Driver Ports - Inbound/Primary port abstractions.

Exports all driver port interfaces (ports that DES exposes to callers).
"""

from src.des.application.orchestrator import HookPort
from src.des.ports.driver_ports.validator_port import ValidatorPort


__all__ = [
    "HookPort",
    "ValidatorPort",
]
