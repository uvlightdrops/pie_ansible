---
project: pie_ansible
scope: architecture
created: null
updated: "2026-11-20 12"
update_reason: "Image-Quelle und Stand des lokalen Testaufbaus dokumentiert."
status: draft
---

# Umsetzungsplan

## Ablagestruktur [ablagestruktur]

```yaml block-meta
updated: "2026-11-20 11"
status: active
relations: []
```

| Pfad | Inhalt |
|---|---|
| `sources/` | Freigegebene Ausgangsmaterialien und Herkunftsnachweise, getrennt von den Projektkonfigurationen. |
| `sources/docker/` | Verzeichnis der verwendeten Container-Images mit Herkunft, Tag und Digest. |
| `sources/docker/exports/` | Lokale Image-Exporte für die Offline-Nutzung; von der Git-Versionierung ausgeschlossen. |
| `config/elasticsearch/` | Versionierte Konfigurationen für den Testaufbau, ohne Zugangsdaten. |
| `doc/architecture/` | Architekturentscheidungen und Umsetzungsplanung. |
| `doc/network/` | Geplante Netzabschnitte, Sicherheitszonen und erlaubte Verbindungen der Simulation. |

Weitere Verzeichnisse entstehen erst, wenn es dafür konkrete Inhalte gibt.
Reale Inventare, Zugangsdaten und ungeprüfte interne Unterlagen gehören nicht
in die Projektablage.

## Docker-Images [docker-images]

```yaml block-meta
updated: "2026-11-20 12"
status: active
relations: []
```

Der erste Test verwendet das offizielle Elasticsearch-Image 9.4.2 aus der
Elastic-Registry. Registry, Versions-Tag und Digest stehen in
[`elasticsearch-image.yaml`](../../sources/docker/elasticsearch-image.yaml);
Compose übernimmt die Referenz aus dieser Datei. Der Digest fixiert die
Manifestliste für `linux/amd64` und `linux/arm64`. Das Image wird aus der
Registry geladen; ein lokaler Export ist für den ersten Aufbau nicht nötig.

## Reihenfolge der Umsetzung [reihenfolge]

```yaml block-meta
updated: "2026-11-20 12"
status: draft
relations: []
```

1. Das Docker-Image ist mit Version, Herkunft und Digest festgelegt.
2. Der lokale Compose-Aufbau und die Elasticsearch-Konfiguration sind
   angelegt. Start und Voraussetzungen stehen in der [README](../../README.md).
   Minikube ist dafür nicht erforderlich.
3. Der lokale Testaufbau hat die Betriebsbereitschaft erreicht und ein
   synthetisches Dokument erfolgreich indexiert und wiedergefunden.
4. Die geplanten Netzabschnitte und erlaubten Verbindungen dokumentieren,
   sobald die freigegebenen Netzunterlagen vorliegen. Daraus ableiten,
   welche Verbindungen in späteren Tests nachgebildet werden sollen.

## Abgrenzung des ersten Aufbaus [abgrenzung]

```yaml block-meta
updated: "2026-11-20 11"
status: active
relations: []
```

Für den ersten Meilenstein genügt eine lokale Elasticsearch-Instanz. Die
Anbindung an das Java-DMS, die Simulation aller vier Umgebungen und
Lasttests sind nicht Teil dieses Schritts. Aus Ansible-Unterlagen werden
zunächst nur die für den jeweiligen Test benötigten betrieblichen Eckdaten
in Form von freigegebenen Angaben oder fiktiven Werten übernommen.
