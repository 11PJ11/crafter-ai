"""Backward compatibility import for ValidatorPort and ValidationResult.

Re-exports ValidatorPort and ValidationResult from driver_ports for backward compatibility with old import paths.
Old code using: from src.des.ports.validator_port import ValidatorPort, ValidationResult
Will continue to work with this module.
"""

from src.des.ports.driver_ports.validator_port import ValidatorPort, ValidationResult

__all__ = ["ValidatorPort", "ValidationResult"]
