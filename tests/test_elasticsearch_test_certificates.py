import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "elasticsearch_test_certificates.py"


class TestCertificates(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name) / "certificates"

    def run_script(self, *args):
        return subprocess.run(
            ["python3", str(SCRIPT), "--base-dir", str(self.base), *args],
            capture_output=True, text=True, check=False,
        )

    def test_create_ca_and_hosts_without_overwriting(self):
        self.assertEqual(self.run_script("init-ca").returncode, 0)
        self.assertNotEqual(self.run_script("init-ca").returncode, 0)
        host_dir = self.base / "elastic.example.org"
        host_dir.mkdir()
        (host_dir / "unrelated").write_text("preserve", encoding="utf-8")
        result = self.run_script(
            "issue", "--host", "elastic.example.org",
            "--san", "DNS:elastic.example.org", "--san", "IP:192.0.2.10",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((host_dir / "unrelated").read_text(encoding="utf-8"), "preserve")
        for key in (self.base / ".test-ca" / "ca.key", host_dir / "elasticsearch.key"):
            self.assertEqual(os.stat(key).st_mode & 0o777, 0o600)
        cert = host_dir / "elasticsearch.crt"
        details = subprocess.check_output(
            ["openssl", "x509", "-in", str(cert), "-noout", "-ext", "subjectAltName"],
            text=True,
        )
        self.assertIn("DNS:elastic.example.org", details)
        self.assertIn("IP Address:192.0.2.10", details)
        previous = cert.read_bytes()
        self.assertNotEqual(
            self.run_script("issue", "--host", "elastic.example.org", "--san", "DNS:other.example.org").returncode,
            0,
        )
        self.assertEqual(cert.read_bytes(), previous)
        second = self.run_script("issue", "--host", "other", "--san", "DNS:other.example.org")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotEqual(
            (host_dir / "elasticsearch.key").read_bytes(),
            (self.base / "other" / "elasticsearch.key").read_bytes(),
        )

    def test_reject_invalid_inputs_and_missing_ca(self):
        self.assertNotEqual(self.run_script("issue", "--host", "test", "--san", "IP:not-an-ip").returncode, 0)
        self.assertNotEqual(self.run_script("issue", "--host", "../test", "--san", "DNS:test").returncode, 0)
        self.assertNotEqual(self.run_script("issue", "--host", "test", "--san", "DNS:test").returncode, 0)
        self.assertFalse((self.base / "test").exists())


if __name__ == "__main__":
    unittest.main()
