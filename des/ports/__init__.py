"""Port interfaces for DES hexagonal architecture."""

from des.ports.hook_port import HookPort, HookResult
from des.ports.validator_port import ValidatorPort, ValidationResult
from des.ports.filesystem_port import FileSystemPort
from des.ports.time_provider_port import TimeProvider

__all__ = [
    "HookPort",
    "HookResult",
    "ValidatorPort",
    "ValidationResult",
    "FileSystemPort",
    "TimeProvider",
]
