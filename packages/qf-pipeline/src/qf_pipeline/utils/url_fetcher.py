"""URL fetching and conversion utility for qf-pipeline.

Automatically fetches URLs and converts HTML content to markdown.
"""

import ipaddress
import logging
import re
import socket
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse
from datetime import datetime

import httpx
from markdownify import markdownify as md

logger = logging.getLogger(__name__)


def is_url(source: str) -> bool:
    """Check if source is a URL (https only).

    Args:
        source: String to check

    Returns:
        True if source is a URL (https://)
    """
    if not source:
        return False
    return source.startswith('https://')


def _is_private_ip(hostname: str) -> bool:
    """Check if hostname resolves to a private/reserved IP address (SSRF prevention)."""
    try:
        # Resolve hostname to IP
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip = ipaddress.ip_address(sockaddr[0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
    except (socket.gaierror, ValueError):
        return True  # Block unresolvable hostnames
    return False


_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_MAX_REDIRECTS = 5


def _validate_fetch_url(url: str) -> Optional[str]:
    """Validate that a URL is safe to fetch.

    Enforces HTTPS and blocks hosts that resolve to private/reserved/internal
    addresses (SSRF prevention). Applied to the initial URL and re-applied to
    every redirect target. Returns an error message, or None if the URL is allowed.
    """
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        return "Only HTTPS URLs are allowed"
    if not parsed.hostname:
        return "Invalid URL: no hostname"
    if _is_private_ip(parsed.hostname):
        logger.warning(f"SSRF blocked: {parsed.hostname} resolves to private/reserved IP")
        return "URL blocked: resolves to a private or internal network address"
    return None


def generate_filename_from_url(url: str, suffix: str = ".md") -> str:
    """Generate a filename from URL.

    Args:
        url: Source URL
        suffix: File extension (default: .md)

    Returns:
        Safe filename derived from URL
    """
    parsed = urlparse(url)

    # Use path or domain as base
    if parsed.path and parsed.path != '/':
        # Clean path: remove leading/trailing slashes, replace / with _
        base = parsed.path.strip('/').replace('/', '_')
        # Remove query params and file extension from URL
        base = base.split('?')[0]
        if '.' in base:
            base = base.rsplit('.', 1)[0]
    else:
        # Use domain
        base = parsed.netloc.replace('.', '_')

    # Clean up: only alphanumeric and underscore
    base = re.sub(r'[^a-zA-Z0-9_-]', '_', base)

    # Truncate if too long
    if len(base) > 50:
        base = base[:50]

    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return f"{base}_{timestamp}{suffix}"


async def fetch_url_to_markdown(
    url: str,
    output_dir: Path,
    filename: Optional[str] = None
) -> Tuple[bool, str, Optional[Path]]:
    """Fetch URL content and save as markdown.

    Args:
        url: URL to fetch
        output_dir: Directory to save the markdown file
        filename: Optional filename (auto-generated if not provided)

    Returns:
        Tuple of (success, message, file_path)
    """
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if not filename:
            filename = generate_filename_from_url(url)

        output_path = output_dir / filename

        # Security: SSRF prevention — validate the initial URL (HTTPS + not private/internal)
        error = _validate_fetch_url(url)
        if error:
            return False, error, None

        logger.info(f"Fetching URL: {url}")

        # Fetch the URL. Redirects are followed MANUALLY so every hop is re-validated:
        # httpx's automatic follow_redirects would let a public host redirect to an
        # internal address (e.g. cloud metadata at 169.254.169.254), bypassing the
        # pre-fetch SSRF check.
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=False,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) QuestionForge/1.0'
            }
        ) as client:
            current_url = url
            for _ in range(_MAX_REDIRECTS + 1):
                response = await client.get(current_url)
                if response.status_code in _REDIRECT_STATUSES:
                    location = response.headers.get('location')
                    if not location:
                        break  # malformed redirect; let raise_for_status handle it
                    current_url = urljoin(current_url, location)
                    redirect_error = _validate_fetch_url(current_url)
                    if redirect_error:
                        logger.warning(f"SSRF blocked on redirect to {current_url}")
                        return False, f"Redirect blocked: {redirect_error}", None
                    continue
                break
            else:
                return False, "Too many redirects", None
            response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        content = response.text

        # Convert HTML to markdown
        if 'html' in content_type.lower():
            logger.info("Converting HTML to markdown")
            markdown_content = html_to_markdown(content, url)
        elif 'markdown' in content_type.lower() or url.endswith('.md'):
            # Already markdown
            markdown_content = content
        else:
            # Treat as plain text, wrap in code block
            markdown_content = f"# Content from {url}\n\n```\n{content}\n```\n"

        # Add source header
        final_content = f"<!-- Source: {url} -->\n<!-- Fetched: {datetime.now().isoformat()} -->\n\n{markdown_content}"

        # Save to file
        output_path.write_text(final_content, encoding='utf-8')

        logger.info(f"Saved to: {output_path}")

        return True, f"URL fetched and saved to {output_path.name}", output_path

    except httpx.HTTPStatusError as e:
        msg = f"HTTP error fetching URL: {e.response.status_code}"
        logger.error(msg)
        return False, msg, None
    except httpx.RequestError as e:
        msg = f"Request error fetching URL: {str(e)}"
        logger.error(msg)
        return False, msg, None
    except Exception as e:
        msg = f"Error fetching URL: {type(e).__name__}: {str(e)}"
        logger.error(msg)
        return False, msg, None


def html_to_markdown(html: str, source_url: str = "") -> str:
    """Convert HTML to clean markdown.

    Args:
        html: HTML content
        source_url: Source URL for context

    Returns:
        Markdown string
    """
    # Use markdownify with sensible defaults
    # Note: Can't use both 'strip' and 'convert' - they're mutually exclusive
    markdown = md(
        html,
        heading_style='ATX',  # Use # style headings
        bullets='-',          # Use - for lists
        strip=['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'iframe']
    )

    # Clean up excessive whitespace
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    markdown = markdown.strip()

    return markdown
