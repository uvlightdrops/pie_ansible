---
project: pie_ansible
scope: guides
created: "2026-11-26 11"
updated: "2026-11-26 15"
update_reason: "Lokales Inventory in der Symlink-Vorgehensweise ergänzt."
status: draft
agent_project: pie_ansible
---

# DevOps security issues

## pip audit

`pip-audit` prüft Python-Pakete auf bekannte Schwachstellen. Die Prüfung
betrifft entweder die installierten Pakete einer Python-Umgebung oder eine
angegebene Requirements-Datei. Sie ersetzt weder eine Codeprüfung noch
die Prüfung von Betriebssystempaketen oder Container-Images.

Für eine Prüfung der aktiven virtuellen Umgebung:

```sh
python -m pip install pip-audit
python -m pip_audit
```

Alternativ kann eine vorhandene Requirements-Datei geprüft werden:

```sh
python -m pip_audit -r requirements.txt
```

Das Projekt enthält derzeit keine Requirements-Datei; der zweite Aufruf
ist daher ein Beispiel. Die Prüfung benötigt Zugriff auf einen
Schwachstellendienst und gegebenenfalls auf Paketquellen. Vorhandene
Zugriffsdaten dürfen nicht in Requirements-Dateien oder Berichte gelangen.
Gefundene Schwachstellen anhand der betroffenen Version und Nutzung
bewerten, Abhängigkeiten aktualisieren und anschließend erneut prüfen.
Ein Audit ohne Treffer garantiert nicht, dass die Umgebung sicher ist.

## Symlink-Vorgehensweise

Umgebungsspezifische Attribute und Zugangsdaten liegen lokal auf dem
Ansible-Controller, nicht im Git-Repository. Ein ignorierter Symlink
verweist auf die passende lokale Datei:

```text
config/ansible/
  inventory.yml -> .local/inventory-dev.yml
config/ansible/group_vars/elastic/
  serviceuser.yml -> .local/serviceuser-dev.yml
  vault.yml       -> .local/vault-dev.yml
```

Auf dem Produktions-Controller zeigen die Links entsprechend auf lokal
angelegte `inventory-prod.yml`, `serviceuser-prod.yml` und `vault-prod.yml`.
Die Gruppenvariablen liegen in ihrem `.local/`-Verzeichnis, damit Ansible
nicht mehrere umgebungsspezifische YAML-Dateien gleichzeitig lädt. Das
Inventory wird standardmäßig über den Link gewählt; ein explizites `-i`
überschreibt die Auswahl. Die Gruppenvariablen gelten für alle
Elastic-Ziele des jeweiligen Controllers.

Symlinks und `.local/` sind durch `.gitignore` ausgeschlossen. Ein Symlink
verschlüsselt keine Daten: Dateien mit Passwörtern werden zusätzlich mit
Ansible Vault verschlüsselt; lokale Dateien und Vault-Passwortdateien
benötigen eingeschränkte Zugriffsrechte. Git-Ignorierregeln schützen
bereits eingecheckte Daten nicht. Konkrete Einrichtungsschritte stehen im
[Elasticsearch-Ansible-Deployment](../architecture/ELASTICSEARCH_ANSIBLE_DEPLOYMENT.md).

## Secret-Scanning

## Umgang mit kompromittierten Zugangsdaten

## Berechtigungen und Zugriffskontrolle

## Container- und Betriebssystempakete

## Sicherheitsprüfungen in CI/CD
