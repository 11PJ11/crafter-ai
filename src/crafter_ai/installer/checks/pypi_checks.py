"""PyPI-specific pre-flight checks for the installer.

This module provides checks that verify PyPI connectivity and package availability
before attempting to install from PyPI. These checks run before the forge:install-pypi command.
"""

import json
import socket
import ssl
import urllib.error
import urllib.request

from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


PYPI_API_URL = "https://pypi.org/pypi"
PYPI_HOST = "pypi.org"
PYPI_PORT = 443
DEFAULT_PACKAGE_NAME = "crafter-ai"


def check_pypi_connectivity() -> CheckResult:
    """Verify PyPI API is reachable.

    Attempts to connect to pypi.org to verify the API is accessible.
    This is a BLOCKING check as installation cannot proceed without PyPI access.

    Returns:
        CheckResult with passed=True if PyPI is reachable, otherwise passed=False
        with remediation guidance.
    """
    try:
        url = f"{PYPI_API_URL}/{DEFAULT_PACKAGE_NAME}/json"
        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                return CheckResult(
                    id="pypi-connectivity",
                    name="PyPI Connectivity",
                    passed=True,
                    severity=CheckSeverity.BLOCKING,
                    message="PyPI API is reachable",
                )
            else:
                return CheckResult(
                    id="pypi-connectivity",
                    name="PyPI Connectivity",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    message=f"PyPI API returned unexpected status: {response.status}",
                    remediation="Check if pypi.org is experiencing issues at https://status.python.org/",
                )
    except urllib.error.URLError as e:
        return CheckResult(
            id="pypi-connectivity",
            name="PyPI Connectivity",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Cannot connect to PyPI: {e.reason}",
            remediation="Check your internet connection and firewall settings. Verify pypi.org is accessible.",
        )
    except TimeoutError:
        return CheckResult(
            id="pypi-connectivity",
            name="PyPI Connectivity",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Connection to PyPI timed out",
            remediation="Check your internet connection speed. PyPI may be experiencing high load.",
        )


def check_package_exists(package_name: str = DEFAULT_PACKAGE_NAME) -> CheckResult:
    """Verify package exists on PyPI.

    Queries the PyPI JSON API to check if the specified package is available.
    This is a BLOCKING check as installation cannot proceed without the package.

    Args:
        package_name: Name of the package to check. Defaults to 'crafter-ai'.

    Returns:
        CheckResult with passed=True if package exists, otherwise passed=False
        with remediation guidance.
    """
    try:
        url = f"{PYPI_API_URL}/{package_name}/json"
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                return CheckResult(
                    id="package-exists",
                    name="Package Exists on PyPI",
                    passed=True,
                    severity=CheckSeverity.BLOCKING,
                    message=f"Package '{package_name}' is available on PyPI",
                )
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return CheckResult(
                id="package-exists",
                name="Package Exists on PyPI",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Package '{package_name}' not found on PyPI",
                remediation=f"Verify the package name is correct. Search PyPI at https://pypi.org/search/?q={package_name}",
            )
        return CheckResult(
            id="package-exists",
            name="Package Exists on PyPI",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Error checking package on PyPI: HTTP {e.code}",
            remediation="Check PyPI status at https://status.python.org/",
        )
    except urllib.error.URLError as e:
        return CheckResult(
            id="package-exists",
            name="Package Exists on PyPI",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Cannot connect to PyPI to verify package: {e.reason}",
            remediation="Check your internet connection and try again.",
        )

    return CheckResult(
        id="package-exists",
        name="Package Exists on PyPI",
        passed=False,
        severity=CheckSeverity.BLOCKING,
        message=f"Unexpected response when checking package '{package_name}'",
        remediation="Try again later or check PyPI status.",
    )


def check_version_available(
    package_name: str = DEFAULT_PACKAGE_NAME, version: str | None = None
) -> CheckResult:
    """Verify specific version exists on PyPI.

    Queries the PyPI JSON API to check if a specific version is available.
    This is a WARNING check as the latest version can be used if not specified.

    Args:
        package_name: Name of the package to check. Defaults to 'crafter-ai'.
        version: Specific version to check. If None, returns warning with latest version info.

    Returns:
        CheckResult with passed=True if version exists or no version specified,
        otherwise passed=False with available versions info.
    """
    if version is None:
        return CheckResult(
            id="version-available",
            name="Version Available on PyPI",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="No specific version requested; latest version will be installed",
        )

    try:
        url = f"{PYPI_API_URL}/{package_name}/json"
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                available_versions = list(data.get("releases", {}).keys())

                if version in available_versions:
                    return CheckResult(
                        id="version-available",
                        name="Version Available on PyPI",
                        passed=True,
                        severity=CheckSeverity.WARNING,
                        message=f"Version {version} of '{package_name}' is available on PyPI",
                    )
                else:
                    latest = data.get("info", {}).get("version", "unknown")
                    return CheckResult(
                        id="version-available",
                        name="Version Available on PyPI",
                        passed=False,
                        severity=CheckSeverity.WARNING,
                        message=f"Version {version} of '{package_name}' not found on PyPI",
                        remediation=f"Available: latest is {latest}. Check releases at https://pypi.org/project/{package_name}/#history",
                    )
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return CheckResult(
                id="version-available",
                name="Version Available on PyPI",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Package '{package_name}' not found on PyPI",
                remediation="Verify the package name is correct.",
            )
        return CheckResult(
            id="version-available",
            name="Version Available on PyPI",
            passed=False,
            severity=CheckSeverity.WARNING,
            message=f"Error checking version on PyPI: HTTP {e.code}",
            remediation="Check PyPI status at https://status.python.org/",
        )
    except urllib.error.URLError as e:
        return CheckResult(
            id="version-available",
            name="Version Available on PyPI",
            passed=False,
            severity=CheckSeverity.WARNING,
            message=f"Cannot connect to PyPI to verify version: {e.reason}",
            remediation="Check your internet connection and try again.",
        )

    return CheckResult(
        id="version-available",
        name="Version Available on PyPI",
        passed=False,
        severity=CheckSeverity.WARNING,
        message="Unexpected error checking version availability",
        remediation="Try again later or check PyPI status.",
    )


def check_pypi_tls() -> CheckResult:
    """Verify TLS certificate is valid for pypi.org.

    Establishes an SSL connection to pypi.org and validates the certificate.
    This is a BLOCKING check as secure communication is required.

    Returns:
        CheckResult with passed=True if TLS certificate is valid,
        otherwise passed=False with remediation guidance.
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((PYPI_HOST, PYPI_PORT), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=PYPI_HOST) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    return CheckResult(
                        id="pypi-tls",
                        name="PyPI TLS Certificate",
                        passed=True,
                        severity=CheckSeverity.BLOCKING,
                        message="PyPI TLS certificate is valid",
                    )
                else:
                    return CheckResult(
                        id="pypi-tls",
                        name="PyPI TLS Certificate",
                        passed=False,
                        severity=CheckSeverity.BLOCKING,
                        message="Could not retrieve PyPI TLS certificate",
                        remediation="There may be a TLS interception proxy. Check your network configuration.",
                    )
    except ssl.SSLCertVerificationError as e:
        return CheckResult(
            id="pypi-tls",
            name="PyPI TLS Certificate",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"PyPI TLS certificate verification failed: {e}",
            remediation="Certificate may be expired, invalid, or intercepted. Check your network security settings.",
        )
    except ssl.SSLError as e:
        return CheckResult(
            id="pypi-tls",
            name="PyPI TLS Certificate",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"SSL error connecting to PyPI: {e}",
            remediation="Check your SSL/TLS configuration and network security settings.",
        )
    except OSError as e:
        return CheckResult(
            id="pypi-tls",
            name="PyPI TLS Certificate",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Cannot connect to PyPI for TLS verification: {e}",
            remediation="Check your internet connection and firewall settings.",
        )


def create_pypi_check_registry() -> CheckRegistry:
    """Create a registry pre-populated with all PyPI checks.

    Returns:
        CheckRegistry with all 4 PyPI checks registered for 'pypi-install' journey.
    """
    registry = CheckRegistry()
    registry.register("pypi-connectivity", check_pypi_connectivity)
    registry.register("package-exists", check_package_exists)
    registry.register("version-available", check_version_available)
    registry.register("pypi-tls", check_pypi_tls)
    return registry
