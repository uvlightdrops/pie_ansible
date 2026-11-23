"""Index a synthetic document and verify that Elasticsearch finds it."""

import json
import subprocess
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


def request(method, path, body=None):
    command = [
        "docker", "compose", "exec", "-T", "elasticsearch",
        "curl", "--silent", "--show-error", "--fail-with-body", "--max-time", "15",
        "--request", method,
    ]
    payload = None
    if body is not None:
        command.extend(["--header", "Content-Type: application/json", "--data-binary", "@-"])
        payload = json.dumps(body)
    command.append(f"http://127.0.0.1:9200/{path}")
    result = subprocess.run(command, cwd=ROOT, input=payload, text=True, stdout=subprocess.PIPE)
    if result.returncode:
        raise SystemExit(f"{method} /{path} fehlgeschlagen: {result.stdout.strip()}")
    return json.loads(result.stdout)


def main():
    index = f"smoke-{uuid4().hex}"
    document = {"titel": "Synthetischer Lieferschein", "typ": "testdokument"}
    request("PUT", f"{index}?wait_for_active_shards=0", {"settings": {"number_of_replicas": 0}})
    try:
        request("PUT", f"{index}/_doc/beispiel?refresh=wait_for&timeout=10s", document)
        result = request("POST", f"{index}/_search", {"query": {"match": {"titel": "Lieferschein"}}})
        hits = result["hits"]["hits"]
        if len(hits) != 1 or hits[0]["_id"] != "beispiel" or hits[0]["_source"] != document:
            raise SystemExit(f"Unerwartetes Suchergebnis: {hits}")
    finally:
        request("DELETE", index)
    print("Elasticsearch: Testdokument erfolgreich indexiert und gefunden.")


if __name__ == "__main__":
    main()
