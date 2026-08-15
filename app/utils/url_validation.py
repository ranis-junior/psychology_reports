import ipaddress
import socket
from http import HTTPStatus
from urllib.parse import urlparse

from fastapi import HTTPException


def _validate_ip(ip_str: str) -> None:
    ip = ipaddress.ip_address(ip_str)
    if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
            or ip.is_reserved or ip.is_unspecified):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='URL resolves to a private/reserved address and is not allowed.',
        )


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Only http and https URLs are supported.',
        )
    if not parsed.hostname:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid URL.',
        )
    if parsed.port and parsed.port not in (80, 443):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Only ports 80 and 443 are supported.',
        )

    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == 'https' else 80))
    except socket.gaierror:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Could not resolve URL host.',
        )

    for info in infos:
        _validate_ip(info[4][0])