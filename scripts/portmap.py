#!/usr/bin/env python3
"""
portmap.py - Container Port Map Visualization

Parses `podman ps` (or `docker ps`) output and generates:
  1. A Unicode box-drawing table of port mappings
  2. A terminal flowchart showing container connectivity

Usage:
    podman ps | python portmap.py
    podman ps --format '{{.ID}}\t{{.Names}}\t{{.Ports}}\t{{.Status}}\t{{.Image}}' | python portmap.py
    python portmap.py < dump.txt

Pure Python stdlib — no external dependencies.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field


# ── ANSI colors ──────────────────────────────────────────────────────────────

USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(t: str) -> str:
    return _c("1", t)


def cyan(t: str) -> str:
    return _c("36", t)


def green(t: str) -> str:
    return _c("32", t)


def yellow(t: str) -> str:
    return _c("33", t)


def magenta(t: str) -> str:
    return _c("35", t)


def dim(t: str) -> str:
    return _c("2", t)


def red(t: str) -> str:
    return _c("31", t)


# ── Data model ───────────────────────────────────────────────────────────────


@dataclass
class PortMapping:
    host_ip: str  # e.g. "0.0.0.0"
    host_port: int
    container_port: int
    protocol: str  # "tcp" or "udp"

    @property
    def display_host(self) -> str:
        return f"{self.host_ip}:{self.host_port}"

    @property
    def display_arrow(self) -> str:
        proto = "" if self.protocol == "tcp" else f"/{self.protocol}"
        if self.host_port == self.container_port:
            return f":{self.host_port}{proto}"
        return f"{self.host_ip}:{self.host_port}→{self.container_port}{proto}"


@dataclass
class Container:
    id: str
    name: str
    image: str
    status: str
    ports: list[PortMapping] = field(default_factory=list)
    is_host_network: bool = False

    @property
    def short_image(self) -> str:
        """Trim registry prefixes like docker.io/library/"""
        img = self.image
        for prefix in ("docker.io/library/", "docker.io/", "localhost/"):
            if img.startswith(prefix):
                img = img[len(prefix) :]
        return img


# ── Parsing ──────────────────────────────────────────────────────────────────

PORT_RE = re.compile(
    r"(?:(?P<hip>[\d.]+|\[::\]):)?(?P<hport>\d+)->(?P<cport>\d+)(?:/(?P<proto>\w+))?"
)


def parse_ports(port_str: str) -> tuple[list[PortMapping], bool]:
    """Parse a ports string, return (mappings, is_host_network)."""
    port_str = port_str.strip()
    if not port_str or port_str == "-":
        return [], False

    mappings: list[PortMapping] = []
    for m in PORT_RE.finditer(port_str):
        hip = m.group("hip") or "0.0.0.0"
        if hip == "[::]":
            hip = "[::]"
        mappings.append(
            PortMapping(
                host_ip=hip,
                host_port=int(m.group("hport")),
                container_port=int(m.group("cport")),
                protocol=m.group("proto") or "tcp",
            )
        )
    return mappings, False


def _detect_column_positions(header: str) -> dict[str, tuple[int, int | None]]:
    """Detect column start positions from the header line of `podman ps` output."""
    cols_ordered = ["CONTAINER ID", "IMAGE", "COMMAND", "CREATED", "STATUS", "PORTS", "NAMES"]
    positions: dict[str, tuple[int, int | None]] = {}
    found: list[tuple[str, int]] = []
    for col in cols_ordered:
        idx = header.find(col)
        if idx != -1:
            found.append((col, idx))
    found.sort(key=lambda x: x[1])
    for i, (col, start) in enumerate(found):
        end = found[i + 1][1] if i + 1 < len(found) else None
        positions[col] = (start, end)
    return positions


def _extract_field(line: str, positions: dict, col: str) -> str:
    if col not in positions:
        return ""
    start, end = positions[col]
    if end is None:
        return line[start:].strip()
    return line[start:end].strip()


def parse_tabular(lines: list[str]) -> list[Container]:
    """Parse standard `podman ps` / `docker ps` tabular output."""
    header = lines[0]
    positions = _detect_column_positions(header)
    if "NAMES" not in positions and "CONTAINER ID" not in positions:
        return []

    containers: list[Container] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cid = _extract_field(line, positions, "CONTAINER ID")
        name = _extract_field(line, positions, "NAMES")
        image = _extract_field(line, positions, "IMAGE")
        status = _extract_field(line, positions, "STATUS")
        port_str = _extract_field(line, positions, "PORTS")

        if not cid and not name:
            continue

        ports, is_host = parse_ports(port_str)
        containers.append(
            Container(
                id=cid,
                name=name or cid[:12],
                image=image,
                status=status,
                ports=ports,
                is_host_network=is_host,
            )
        )
    return containers


def parse_tsv(lines: list[str]) -> list[Container]:
    """Parse tab-separated format from --format."""
    containers: list[Container] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        cid = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else cid[:12]
        port_str = parts[2] if len(parts) > 2 else ""
        status = parts[3] if len(parts) > 3 else ""
        image = parts[4] if len(parts) > 4 else ""

        ports, is_host = parse_ports(port_str)
        containers.append(
            Container(
                id=cid, name=name, image=image, status=status,
                ports=ports, is_host_network=is_host,
            )
        )
    return containers


def detect_host_network(containers: list[Container]) -> None:
    """Heuristic: if status or ports column mentions 'host', flag it."""
    for c in containers:
        # No ports but running — could be host network
        # We can't be 100% sure from ps output alone, but we try
        pass


def parse_input(text: str) -> list[Container]:
    """Auto-detect format and parse."""
    lines = text.splitlines()
    lines = [l for l in lines if l.strip()]
    if not lines:
        return []

    # Check if it's standard tabular output (header starts with CONTAINER ID)
    header = lines[0].strip()
    if header.startswith("CONTAINER ID") or header.startswith("CONTAINER"):
        return parse_tabular(lines)

    # Check if tab-separated
    if "\t" in lines[0]:
        return parse_tsv(lines)

    # Fallback: try tabular anyway (maybe header has different casing)
    upper = header.upper()
    if "CONTAINER" in upper or "IMAGE" in upper or "NAMES" in upper:
        return parse_tabular(lines)

    # Last resort: try TSV
    return parse_tsv(lines)


# ── Rendering ────────────────────────────────────────────────────────────────


def _pad(text: str, width: int) -> str:
    """Pad text to width, accounting for ANSI codes."""
    visible = re.sub(r"\033\[[^m]*m", "", text)
    padding = max(0, width - len(visible))
    return text + " " * padding


def render_table(containers: list[Container]) -> str:
    """Render the port map summary table."""
    # Collect rows: (port_display, container_name, status, image)
    rows: list[tuple[str, str, str, str]] = []
    for c in containers:
        if c.ports:
            for p in sorted(c.ports, key=lambda x: x.host_port):
                proto_suffix = "" if p.protocol == "tcp" else f"/{p.protocol}"
                port_display = f"{p.host_ip}:{p.host_port}→{p.container_port}{proto_suffix}"
                rows.append((port_display, c.name, c.status, c.short_image))
        elif c.is_host_network:
            rows.append(("HOST NETWORK", c.name, c.status, c.short_image))
        else:
            rows.append(("(none)", c.name, c.status, c.short_image))

    rows.sort(key=lambda r: (
        0 if r[0] not in ("(none)", "HOST NETWORK") else 1,
        int(re.search(r":(\d+)", r[0]).group(1)) if re.search(r":(\d+)", r[0]) else 99999,
        r[1],
    ))

    if not rows:
        return "  No containers found.\n"

    headers = ("Port", "Container", "Status", "Image")
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Add padding
    col_widths = [w + 2 for w in col_widths]
    total_inner = sum(col_widths) + len(col_widths) - 1  # +separators

    out: list[str] = []

    # Title bar
    title = "PORT MAP SUMMARY"
    title_w = total_inner + 2
    out.append(f"╔{'═' * title_w}╗")
    out.append(f"║{bold(cyan(title.center(title_w)))}║")

    # Header separator
    out.append("╠" + "╦".join("═" * (w + 2) for w in col_widths) + "╣")
    # Header row
    hdr_cells = []
    for i, h in enumerate(headers):
        hdr_cells.append(f" {_pad(bold(h), col_widths[i])} ")
    out.append("║" + "║".join(hdr_cells) + "║")
    # Header-body separator
    out.append("╠" + "╬".join("═" * (w + 2) for w in col_widths) + "╣")

    # Data rows
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            if i == 0:  # Port
                display = cyan(cell) if cell not in ("(none)", "HOST NETWORK") else (
                    yellow(cell) if cell == "HOST NETWORK" else dim(cell)
                )
            elif i == 1:  # Container
                display = green(cell)
            elif i == 2:  # Status
                display = yellow(cell) if "Up" in cell else red(cell)
            else:  # Image
                display = magenta(cell)
            cells.append(f" {_pad(display, col_widths[i])} ")
        out.append("║" + "║".join(cells) + "║")

    # Bottom border
    out.append("╚" + "╩".join("═" * (w + 2) for w in col_widths) + "╝")

    return "\n".join(out) + "\n"


def render_diagram(containers: list[Container]) -> str:
    """Render the flow diagram."""
    # Separate: containers with ports, host-network, no ports
    with_ports: list[Container] = []
    host_net: list[Container] = []
    no_ports: list[Container] = []

    for c in containers:
        if c.ports:
            with_ports.append(c)
        elif c.is_host_network:
            host_net.append(c)
        else:
            no_ports.append(c)

    # Sort by lowest port
    with_ports.sort(key=lambda c: min(p.host_port for p in c.ports))

    out: list[str] = []
    out.append(bold("\n  CONTAINER FLOW"))
    out.append(dim("  ─" * 20))

    def draw_box(c: Container, port_labels: list[str], tag: str = "") -> list[str]:
        name_line = f"  {c.name}"
        image_line = f"  ({c.short_image})"
        lines_content = [name_line, image_line]
        if tag:
            lines_content.append(f"  {tag}")

        box_width = max(len(l) for l in lines_content) + 2
        box_width = max(box_width, 20)

        box_lines: list[str] = []
        top = f"  ┌{'─' * box_width}┐"
        bot = f"  └{'─' * box_width}┘"

        box_lines.append(top)
        for j, line in enumerate(lines_content):
            padded = line + " " * (box_width - len(line))
            if j == 0:
                # Show port arrows on the first content line
                if port_labels:
                    arrows = ", ".join(port_labels)
                    box_lines.append(f"  │{green(padded)}│──→ {cyan(arrows)}")
                else:
                    box_lines.append(f"  │{green(padded)}│")
            elif j == 1:
                box_lines.append(f"  │{dim(padded)}│")
            else:
                box_lines.append(f"  │{yellow(padded)}│")
        box_lines.append(bot)
        return box_lines

    for i, c in enumerate(with_ports):
        port_labels = []
        for p in sorted(c.ports, key=lambda x: x.host_port):
            port_labels.append(p.display_arrow)
        out.extend(draw_box(c, port_labels))
        if i < len(with_ports) - 1 or host_net or no_ports:
            out.append(f"  {'':8}│")

    if host_net:
        out.append(dim("  ── HOST NETWORK ──"))
        for i, c in enumerate(host_net):
            out.extend(draw_box(c, [], tag="⚡ HOST NETWORK"))
            if i < len(host_net) - 1 or no_ports:
                out.append(f"  {'':8}│")

    if no_ports:
        out.append(dim("  ── NO PORTS ──"))
        for i, c in enumerate(no_ports):
            out.extend(draw_box(c, [], tag="(no exposed ports)"))
            if i < len(no_ports) - 1:
                out.append(f"  {'':8}│")

    out.append("")
    return "\n".join(out) + "\n"


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    if sys.stdin.isatty():
        print(dim("Paste podman ps output (Ctrl+D when done):"), file=sys.stderr)

    text = sys.stdin.read()
    if not text.strip():
        print("No input received.", file=sys.stderr)
        sys.exit(1)

    containers = parse_input(text)
    if not containers:
        print("Could not parse any containers from input.", file=sys.stderr)
        sys.exit(1)

    print()
    print(render_table(containers))
    print(render_diagram(containers))

    # Summary
    total_ports = sum(len(c.ports) for c in containers)
    print(dim(f"  {len(containers)} containers, {total_ports} port mappings\n"))


if __name__ == "__main__":
    main()
