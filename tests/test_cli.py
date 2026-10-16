"""
Unit tests for DeveloperOS Unified CLI (devos).
Tests all subcommands: json, jwt, hash, b64, uuid, cron, list, and the main entrypoint.
"""

import base64
import datetime
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from devos.cli import main
from devos.commands import (
    b64_cmd,
    cron_cmd,
    hash_cmd,
    json_cmd,
    jwt_cmd,
    list_cmd,
    uuid_cmd,
)


def create_sample_jwt(header: dict, payload: dict) -> str:
    """Helper to generate an unsigned or sample JWT."""
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(b"sample_mock_signature_123456").decode().rstrip("=")
    return f"{h_b64}.{p_b64}.{sig}"


class TestDevOSCLI(unittest.TestCase):
    """Main test suite covering all CLI subcommands and functions."""

    # --------------------------------------------------------------------------
    # Main CLI Runner & Global Options
    # --------------------------------------------------------------------------
    def test_cli_no_args_shows_banner_and_help(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main([])
        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn("DeveloperOS Unified Developer CLI", output)
        self.assertIn("Subcommands", output)

    def test_cli_version_flag(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            with self.assertRaises(SystemExit) as cm:
                main(["--version"])
            self.assertEqual(cm.exception.code, 0)
        output = stdout.getvalue()
        self.assertIn("devos 1.0.0", output)

    def test_cli_invalid_subcommand(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            with self.assertRaises(SystemExit) as cm:
                main(["nonexistent-command"])
            self.assertNotEqual(cm.exception.code, 0)

    # --------------------------------------------------------------------------
    # Subcommand: json
    # --------------------------------------------------------------------------
    def test_json_format_default(self):
        stdout = io.StringIO()
        raw = '{"name":"devos","version":1}'
        with patch("sys.stdout", stdout):
            code = main(["json", raw])
        self.assertEqual(code, 0)
        parsed = json.loads(stdout.getvalue())
        self.assertEqual(parsed["name"], "devos")
        self.assertIn("  \"name\": \"devos\"", stdout.getvalue())

    def test_json_format_custom_indent(self):
        stdout = io.StringIO()
        raw = '{"tool":"json"}'
        with patch("sys.stdout", stdout):
            code = main(["json", "-i", "4", raw])
        self.assertEqual(code, 0)
        self.assertIn("    \"tool\": \"json\"", stdout.getvalue())

    def test_json_sort_keys(self):
        stdout = io.StringIO()
        raw = '{"z": 1, "a": 2, "m": 3}'
        with patch("sys.stdout", stdout):
            code = main(["json", "-s", raw])
        self.assertEqual(code, 0)
        lines = [line.strip() for line in stdout.getvalue().strip().splitlines() if ":" in line]
        self.assertTrue(lines[0].startswith('"a"'))
        self.assertTrue(lines[1].startswith('"m"'))
        self.assertTrue(lines[2].startswith('"z"'))

    def test_json_minify(self):
        stdout = io.StringIO()
        raw = '{\n  "name": "developer-os",\n  "active": true\n}'
        with patch("sys.stdout", stdout):
            code = main(["json", "-m", raw])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), '{"name":"developer-os","active":true}')

    def test_json_validate_valid(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["json", "-v", '{"status": "ok", "count": 42}'])
        self.assertEqual(code, 0)
        self.assertIn("[VALID]", stdout.getvalue())

    def test_json_validate_invalid(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            code = main(["json", "-v", '{"broken": missing_quotes}'])
        self.assertEqual(code, 1)
        self.assertIn("[INVALID]", stderr.getvalue())

    def test_json_format_invalid_syntax_error(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            code = main(["json", '{invalid'])
        self.assertEqual(code, 1)
        self.assertIn("[ERROR] Invalid JSON", stderr.getvalue())

    def test_json_read_from_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            tf.write('{"file_read": true}')
            tf_name = tf.name

        try:
            stdout = io.StringIO()
            with patch("sys.stdout", stdout):
                code = main(["json", tf_name])
            self.assertEqual(code, 0)
            parsed = json.loads(stdout.getvalue())
            self.assertTrue(parsed["file_read"])
        finally:
            if os.path.exists(tf_name):
                os.unlink(tf_name)

    # --------------------------------------------------------------------------
    # Subcommand: jwt
    # --------------------------------------------------------------------------
    def test_jwt_decode_and_inspect(self):
        token = create_sample_jwt(
            {"alg": "HS256", "typ": "JWT"},
            {"sub": "user_42", "role": "admin", "iat": 1700000000},
        )
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["jwt", token])
        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn("DeveloperOS JWT Inspector", output)
        self.assertIn("user_42", output)
        self.assertIn("HS256", output)

    def test_jwt_header_only(self):
        token = create_sample_jwt({"alg": "RS256", "kid": "key_1"}, {"sub": "test"})
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["jwt", "--header", token])
        self.assertEqual(code, 0)
        header = json.loads(stdout.getvalue())
        self.assertEqual(header["alg"], "RS256")
        self.assertEqual(header["kid"], "key_1")

    def test_jwt_claims_only(self):
        token = create_sample_jwt({"alg": "HS256"}, {"user": "alice", "aud": "developer-os"})
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["jwt", "-c", token])
        self.assertEqual(code, 0)
        claims = json.loads(stdout.getvalue())
        self.assertEqual(claims["user"], "alice")
        self.assertEqual(claims["aud"], "developer-os")

    def test_jwt_json_output(self):
        token = create_sample_jwt({"alg": "HS256"}, {"sub": "tester"})
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["jwt", "--json", token])
        self.assertEqual(code, 0)
        parsed = json.loads(stdout.getvalue())
        self.assertIn("header", parsed)
        self.assertIn("payload", parsed)
        self.assertIn("timestamps", parsed)

    def test_jwt_verify_expiration_active(self):
        future_ts = datetime.datetime.now(datetime.timezone.utc).timestamp() + 3600
        token = create_sample_jwt({"alg": "HS256"}, {"sub": "active_user", "exp": future_ts})
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["jwt", "--verify-exp", token])
        self.assertEqual(code, 0)
        self.assertIn("[VALID]", stdout.getvalue())

    def test_jwt_verify_expiration_expired(self):
        past_ts = datetime.datetime.now(datetime.timezone.utc).timestamp() - 3600
        token = create_sample_jwt({"alg": "HS256"}, {"sub": "expired_user", "exp": past_ts})
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            code = main(["jwt", "--verify-exp", token])
        self.assertEqual(code, 1)
        self.assertIn("[EXPIRED]", stderr.getvalue())

    def test_jwt_malformed_token(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            code = main(["jwt", "invalid.jwt"])
        self.assertEqual(code, 1)
        self.assertIn("[ERROR]", stderr.getvalue())

    # --------------------------------------------------------------------------
    # Subcommand: hash
    # --------------------------------------------------------------------------
    def test_hash_sha256_string(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["hash", "-a", "sha256", "-t", "hello"])
        self.assertEqual(code, 0)
        # sha256("hello") = 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
        self.assertEqual(stdout.getvalue().strip(), "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")

    def test_hash_sha512(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["hash", "-a", "sha512", "-t", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(len(stdout.getvalue().strip()), 128)

    def test_hash_md5(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["hash", "-a", "md5", "-t", "hello"])
        self.assertEqual(code, 0)
        # md5("hello") = 5d41402abc4b2a76b9719d911017c592
        self.assertEqual(stdout.getvalue().strip(), "5d41402abc4b2a76b9719d911017c592")

    def test_hash_sha1(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["hash", "-a", "sha1", "-t", "hello"])
        self.assertEqual(code, 0)
        # sha1("hello") = aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
        self.assertEqual(stdout.getvalue().strip(), "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")

    def test_hash_uppercase(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["hash", "-a", "sha256", "--upper", "-t", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824")

    def test_hash_all_algorithms(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["hash", "-a", "all", "-t", "hello"])
        self.assertEqual(code, 0)
        val = stdout.getvalue()
        self.assertIn("SHA-256", val)
        self.assertIn("SHA-512", val)
        self.assertIn("SHA-1", val)
        self.assertIn("MD5", val)

    def test_hash_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            tf.write("hello")
            tf_name = tf.name

        try:
            stdout = io.StringIO()
            with patch("sys.stdout", stdout):
                code = main(["hash", "-a", "sha256", "-f", tf_name])
            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue().strip(), "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")
        finally:
            if os.path.exists(tf_name):
                os.unlink(tf_name)

    def test_hash_json_output(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["hash", "-a", "sha256", "--json", "-t", "developer-os"])
        self.assertEqual(code, 0)
        parsed = json.loads(stdout.getvalue())
        self.assertIn("hashes", parsed)
        self.assertIn("sha256", parsed["hashes"])

    # --------------------------------------------------------------------------
    # Subcommand: b64
    # --------------------------------------------------------------------------
    def test_b64_encode_string(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["b64", "hello world"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "aGVsbG8gd29ybGQ=")

    def test_b64_decode_string(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["b64", "-d", "aGVsbG8gd29ybGQ="])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "hello world")

    def test_b64_decode_missing_padding(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["b64", "-d", "aGVsbG8gd29ybGQ"])  # No '=' padding
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "hello world")

    def test_b64_url_safe(self):
        test_bytes = b"\xfb\xff\xfe"
        encoded_url = b64_cmd.encode_b64(test_bytes, url_safe=True)
        self.assertNotIn("+", encoded_url)
        self.assertNotIn("/", encoded_url)
        decoded = b64_cmd.decode_b64(encoded_url, url_safe=True)
        self.assertEqual(decoded, test_bytes)

    def test_b64_file_roundtrip(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as tf_in:
            tf_in.write(b"DeveloperOS Zero-Dependency Test")
            in_name = tf_in.name

        encoded_file = in_name + ".enc"
        decoded_file = in_name + ".dec"

        try:
            # Encode file
            code1 = main(["b64", "-f", in_name, "-o", encoded_file])
            self.assertEqual(code1, 0)

            # Decode file
            code2 = main(["b64", "-d", "-f", encoded_file, "-o", decoded_file])
            self.assertEqual(code2, 0)

            with open(decoded_file, "rb") as f:
                content = f.read()
            self.assertEqual(content, b"DeveloperOS Zero-Dependency Test")
        finally:
            for p in (in_name, encoded_file, decoded_file):
                if os.path.exists(p):
                    os.unlink(p)

    # --------------------------------------------------------------------------
    # Subcommand: uuid
    # --------------------------------------------------------------------------
    def test_uuid_single_default(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["uuid"])
        self.assertEqual(code, 0)
        lines = stdout.getvalue().strip().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(len(lines[0]), 36)
        self.assertEqual(lines[0].count("-"), 4)

    def test_uuid_multiple_count(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["uuid", "-n", "5"])
        self.assertEqual(code, 0)
        lines = stdout.getvalue().strip().splitlines()
        self.assertEqual(len(lines), 5)
        # All unique
        self.assertEqual(len(set(lines)), 5)

    def test_uuid_uppercase(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["uuid", "-u"])
        self.assertEqual(code, 0)
        val = stdout.getvalue().strip()
        self.assertEqual(val, val.upper())

    def test_uuid_no_hyphens(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["uuid", "--no-hyphens"])
        self.assertEqual(code, 0)
        val = stdout.getvalue().strip()
        self.assertEqual(len(val), 32)
        self.assertNotIn("-", val)

    def test_uuid_json_format(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["uuid", "-n", "3", "--json"])
        self.assertEqual(code, 0)
        arr = json.loads(stdout.getvalue())
        self.assertIsInstance(arr, list)
        self.assertEqual(len(arr), 3)

    # --------------------------------------------------------------------------
    # Subcommand: cron
    # --------------------------------------------------------------------------
    def test_cron_every_15_minutes(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["cron", "*/15 * * * *", "-n", "4", "--from", "2026-01-01T10:00:00"])
        self.assertEqual(code, 0)
        val = stdout.getvalue()
        self.assertIn("10:15:00", val)
        self.assertIn("10:30:00", val)
        self.assertIn("10:45:00", val)
        self.assertIn("11:00:00", val)

    def test_cron_aliases(self):
        for alias in ["@hourly", "@daily", "@weekly", "@monthly", "@yearly"]:
            stdout = io.StringIO()
            with patch("sys.stdout", stdout):
                code = main(["cron", alias, "-n", "2"])
            self.assertEqual(code, 0)
            self.assertIn("Upcoming 2 execution times", stdout.getvalue())

    def test_cron_json_output(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["cron", "0 12 * * 1-5", "--json", "-n", "3"])
        self.assertEqual(code, 0)
        data = json.loads(stdout.getvalue())
        self.assertIn("expression", data)
        self.assertIn("explanation", data)
        self.assertIn("next_runs", data)
        self.assertEqual(len(data["next_runs"]), 3)

    def test_cron_invalid_expression(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            code = main(["cron", "invalid cron expr"])
        self.assertEqual(code, 1)
        self.assertIn("[ERROR]", stderr.getvalue())

    # --------------------------------------------------------------------------
    # Subcommand: list
    # --------------------------------------------------------------------------
    def test_list_all_tools(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["list"])
        self.assertEqual(code, 0)
        val = stdout.getvalue()
        self.assertIn("DeveloperOS Tools Ecosystem Directory", val)
        self.assertIn("crypto-hash-generator", val)
        self.assertIn("api-sentinel", val)

    def test_list_filter_category(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["list", "-c", "security"])
        self.assertEqual(code, 0)
        val = stdout.getvalue()
        self.assertIn("crypto-hash-generator", val)
        self.assertIn("SECURITY", val)

    def test_list_search_query(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["list", "-s", "cron"])
        self.assertEqual(code, 0)
        val = stdout.getvalue()
        self.assertIn("cloud-cron-parser", val)

    def test_list_json_format(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["list", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(stdout.getvalue())
        self.assertIn("ecosystem", data)
        self.assertIn("tools", data)
        self.assertGreater(data["total_tools"], 0)

    def test_list_verbose(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = main(["list", "-s", "jwt", "-v"])
        self.assertEqual(code, 0)
        self.assertIn("About:", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
