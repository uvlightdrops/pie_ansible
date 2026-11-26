#!/usr/bin/env python3
"""Create a temporary CA and per-host Elasticsearch certificates."""

import argparse
import ipaddress
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOST_PATTERN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\Z")
DNS_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\Z")


def openssl(*args):
    result = subprocess.run(
        ["openssl", *map(str, args)], text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(f"OpenSSL fehlgeschlagen: {result.stderr.strip()}")


def subject_alt_name(value):
    kind, separator, name = value.partition(":")
    if not separator or not name:
        raise argparse.ArgumentTypeError("SAN als DNS:hostname oder IP:adresse angeben")
    if kind == "IP":
        try:
            return f"IP:{ipaddress.ip_address(name)}"
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"Ungültige IP-Adresse: {name}") from exc
    if kind == "DNS" and len(name) <= 253 and all(
        DNS_LABEL.fullmatch(label) for label in name.split(".")
    ):
        return f"DNS:{name}"
    raise argparse.ArgumentTypeError(f"Ungültiger SAN-Eintrag: {value}")


def create_directory(path):
    try:
        path.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise RuntimeError(f"{path} existiert bereits; es wird nichts überschrieben.") from exc


def create_ca(base):
    ca_dir = base / ".test-ca"
    create_directory(ca_dir)
    try:
        openssl(
            "req", "-x509", "-newkey", "rsa:3072", "-noenc",
            "-keyout", ca_dir / "ca.key", "-out", ca_dir / "ca.crt",
            "-days", "30", "-sha256", "-subj", "/CN=Elasticsearch Test CA",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign",
        )
    except (OSError, RuntimeError):
        shutil.rmtree(ca_dir)
        raise
    print(f"Test-CA erstellt: {ca_dir}; privaten CA-Schlüssel schützen.")


def create_host(base, host, sans):
    if not HOST_PATTERN.fullmatch(host) or host in {".", ".."}:
        raise ValueError("Inventory-Hostname darf nur Buchstaben, Ziffern, Punkt, Bindestrich und Unterstrich enthalten.")
    ca_dir = base / ".test-ca"
    ca_cert = ca_dir / "ca.crt"
    ca_key = ca_dir / "ca.key"
    if not ca_cert.is_file() or not ca_key.is_file():
        raise RuntimeError(f"Test-CA fehlt oder ist unvollständig: {ca_dir}")
    openssl("x509", "-in", ca_cert, "-noout", "-checkend", str(7 * 86400))
    host_dir = base / host
    try:
        host_dir.mkdir(mode=0o700)
        created_directory = True
    except FileExistsError:
        created_directory = False
        if host_dir.is_symlink() or not host_dir.is_dir():
            raise RuntimeError(f"Kein reguläres Hostverzeichnis: {host_dir}")
    names = ("elasticsearch.key", "elasticsearch.crt", "ca.crt")
    published = []
    try:
        if any((host_dir / name).exists() or (host_dir / name).is_symlink() for name in names):
            raise RuntimeError(f"Zertifikatsdatei in {host_dir} existiert bereits; es wird nichts überschrieben.")
        with tempfile.TemporaryDirectory(prefix=".elasticsearch-", dir=host_dir) as temporary:
            stage = Path(temporary)
            csr = stage / "elasticsearch.csr"
            extensions = stage / "elasticsearch.ext"
            extensions.write_text(
                "basicConstraints=critical,CA:FALSE\n"
                "keyUsage=critical,digitalSignature,keyEncipherment\n"
                "extendedKeyUsage=serverAuth,clientAuth\n"
                f"subjectAltName={','.join(sans)}\n",
                encoding="ascii",
            )
            openssl(
                "req", "-new", "-newkey", "rsa:3072", "-noenc",
                "-keyout", stage / "elasticsearch.key", "-out", csr,
                "-subj", f"/CN={host}",
            )
            openssl(
                "x509", "-req", "-in", csr, "-CA", ca_cert, "-CAkey", ca_key,
                "-set_serial", str(secrets.randbits(159) + 1),
                "-out", stage / "elasticsearch.crt", "-days", "7",
                "-sha256", "-extfile", extensions,
            )
            openssl("verify", "-CAfile", ca_cert, "-purpose", "sslserver", stage / "elasticsearch.crt")
            openssl("verify", "-CAfile", ca_cert, "-purpose", "sslclient", stage / "elasticsearch.crt")
            shutil.copyfile(ca_cert, stage / "ca.crt")
            for name in names:
                os.link(stage / name, host_dir / name)
                published.append(host_dir / name)
    except (OSError, RuntimeError):
        for path in published:
            path.unlink()
        if created_directory:
            host_dir.rmdir()
        raise
    print(f"Elasticsearch-Testzertifikat für {host} erstellt: {host_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", type=Path, required=True, help="Zertifikatsverzeichnis außerhalb des Repositories")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-ca", help="Einmalig eine Test-CA erstellen")
    issue = commands.add_parser("issue", help="Testzertifikat für einen Inventory-Host erstellen")
    issue.add_argument("--host", required=True, help="Inventory-Hostname")
    issue.add_argument("--san", action="append", required=True, type=subject_alt_name, help="DNS:name oder IP:adresse; mehrfach möglich")
    args = parser.parse_args()

    base = args.base_dir.resolve()
    if base == ROOT or ROOT in base.parents:
        parser.error("Das Zertifikatsverzeichnis muss außerhalb des Repositories liegen.")
    os.umask(0o077)
    try:
        base.mkdir(mode=0o700, parents=True, exist_ok=True)
        if args.command == "init-ca":
            create_ca(base)
        else:
            create_host(base, args.host, args.san)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
