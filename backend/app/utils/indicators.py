import ipaddress
import re
from urllib.parse import urlparse

HASH_REGEX = re.compile(r'^[A-Fa-f0-9]{32}$|^[A-Fa-f0-9]{40}$|^[A-Fa-f0-9]{64}$')
DOMAIN_REGEX = re.compile(
    r'^(?!-)(?:[A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}$'
)


def normalize_input(value: str) -> str:
    return value.strip()


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_hash(value: str) -> bool:
    return bool(HASH_REGEX.match(value))


def is_domain(value: str) -> bool:
    return bool(DOMAIN_REGEX.match(value))


def classify_indicator(value: str) -> str:
    if is_url(value):
        return 'url'
    if is_ip(value):
        return 'ip'
    if is_hash(value):
        return 'hash'
    if is_domain(value):
        return 'domain'
    raise ValueError('Input must be a valid URL, IP address, domain, or file hash.')
