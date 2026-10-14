"""Optional server-side proxy configuration for the Burp lab."""

from __future__ import annotations

import os
import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional
from urllib.parse import urlparse


class ProxyConfigurationError(ValueError):
    """Raised when the opt-in lab proxy configuration is incomplete or invalid."""


@dataclass(frozen=True)
class LabProxyConfig:
    url: Optional[str] = None
    ca_cert: Optional[Path] = None

    @property
    def enabled(self) -> bool:
        return self.url is not None

    @property
    def requests_proxies(self) -> dict[str, str]:
        if not self.url:
            return {}
        return {"http": self.url, "https": self.url}

    def create_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context()
        if self.ca_cert:
            context.load_verify_locations(cafile=str(self.ca_cert))
        return context


def load_lab_proxy_config(
    environ: Optional[Mapping[str, str]] = None,
) -> LabProxyConfig:
    environment = os.environ if environ is None else environ
    proxy_url = environment.get("LAB_PROXY_URL", "").strip()
    ca_cert_value = environment.get("LAB_PROXY_CA_CERT", "").strip()

    if not proxy_url and not ca_cert_value:
        return LabProxyConfig()
    if not proxy_url or not ca_cert_value:
        raise ProxyConfigurationError(
            "LAB_PROXY_URL and LAB_PROXY_CA_CERT must be set together"
        )

    parsed_url = urlparse(proxy_url)
    try:
        port = parsed_url.port
    except ValueError as exc:
        raise ProxyConfigurationError(f"Invalid LAB_PROXY_URL: {exc}") from exc

    if (
        parsed_url.scheme not in {"http", "https"}
        or not parsed_url.hostname
        or port is None
        or parsed_url.path not in {"", "/"}
        or parsed_url.params
        or parsed_url.query
        or parsed_url.fragment
    ):
        raise ProxyConfigurationError(
            "LAB_PROXY_URL must be an http(s) URL with a host and port, "
            "for example http://127.0.0.1:8080"
        )

    ca_cert = Path(ca_cert_value).expanduser().resolve()
    if not ca_cert.is_file():
        raise ProxyConfigurationError(
            f"LAB_PROXY_CA_CERT does not point to a file: {ca_cert}"
        )

    config = LabProxyConfig(url=proxy_url, ca_cert=ca_cert)
    try:
        config.create_ssl_context()
    except (OSError, ssl.SSLError) as exc:
        raise ProxyConfigurationError(
            f"LAB_PROXY_CA_CERT is not a valid CA certificate: {ca_cert}"
        ) from exc

    return config
