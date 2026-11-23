---
project: pie_ansible
scope: architecture
created: null
updated: "2026-11-23 10"
update_reason: "Umgebungen allgemein gehalten, Sicherheitszonen entfernt."
status: draft
---

# Projektskizze zur IT-Simulation

Die geplante Ablagestruktur und die Reihenfolge der Umsetzung stehen im
[Umsetzungsplan](doc/architecture/UMSETZUNGSPLAN.md).

## Entwicklungsziel [entwicklungsziel]

```yaml block-meta
updated: "2026-11-20 11"
status: active
relations: []
```

In einer getrennten Testumgebung sollen Konfigurationen und Skripte für
Elasticsearch und später bei Bedarf für weitere Dienste so weit wie möglich
entwickelt und geprüft werden. Die Simulation bildet dafür die Eigenschaften
der realen IT-Umgebung nach, die das Verhalten der Dienste beeinflussen.
Ergebnisse lassen sich anschließend gezielt auf die Zielumgebung übertragen,
ohne während der Entwicklung auf reale Systeme zugreifen zu müssen.

## Umgebungen [umgebungen]

```yaml block-meta
updated: "2026-11-20 18"
status: active
relations: []
```

Das Modell unterscheidet mehrere Umgebungen. Im Inventar ist erkennbar,
welche Hosts und Dienste welchem Fachbereich und welcher Umgebung zugeordnet
sind. Der erste Aufbau muss nicht alle Umgebungen gleichzeitig ausführen.
Alle Umgebungen im Modell sind Nachbildungen und verweisen nicht auf reale
Systeme.

## Physische und virtuelle Systeme [systemmodell]

```yaml block-meta
updated: "2026-11-20 11"
status: active
relations: []
```

Die Umgebung enthält physische Server und virtuelle Maschinen mit
unterschiedlichen Aufgaben. Ob ein Host physisch oder virtuell ist, wird
zunächst als Attribut im Modell erfasst, ebenso seine Rolle und die
Zuordnung zu einer Umgebung. Für den ersten
Elasticsearch-Aufbau sind Docker-Container vorgesehen. Ob dafür auch eine
tatsächliche virtuelle Maschine nötig ist, hängt davon ab, ob der Test
Eigenschaften des VM-Betriebs prüfen soll.

## Entwicklungsrechner [dev-host]

```yaml block-meta
updated: "2026-11-20 11"
status: active
relations: []
```

Auf dem Entwicklungsrechner sind Docker (CLI-Version 29.9.2) und Minikube
(Version 1.38.0) installiert. Der erste Elasticsearch-Testaufbau soll
direkt mit Docker laufen. Minikube steht für spätere Kubernetes-Tests zur
Verfügung, ist für den ersten Aufbau aber nicht erforderlich.

## Ansible als Vorlage [ansible-vorlagen]

```yaml block-meta
updated: "2026-11-20 11"
status: active
relations: []
```

Die vorhandenen Ansible-Skripte und das Inventar dienen als Quellen für
betriebliche Eckdaten: welche Dienstkonten benötigt werden, wo Basisdienste
laufen oder laufen sollen und wie die Verzeichnisstruktur aufgebaut ist.
Dazu gehören auch Namenskonventionen, Dateipfade und erforderliche
Berechtigungen. Für den Aufbau werden die relevanten Angaben in ein eigenes
Testinventar übertragen; bestehende Playbooks werden nicht ungeprüft gegen
dieses oder das reale Inventar ausgeführt.

## Testdaten und Zugangsdaten [testdaten]

```yaml block-meta
updated: "2026-11-20 11"
status: active
relations: []
```

Der Testaufbau verwendet keine echten Zugangsdaten. Falls Elasticsearch
Anmeldedaten benötigt, werden sie ausschließlich für den Testaufbau erzeugt
und nicht eingecheckt. Für IP-Adressen, Hostnamen und andere interne Angaben
wird je nach Kategorie entschieden, welche Information der Test tatsächlich
braucht und welcher fiktive Wert sie ersetzen kann. Das bloße Ändern eines
Teils einer realen IP-Adresse reicht nicht aus. Struktur und Abhängigkeiten
können mit synthetischen Werten nachgebildet werden.

## Elasticsearch und das Java-DMS [elasticsearch-dms]

```yaml block-meta
updated: "2026-11-20 11"
status: draft
relations: []
```

Das Java-Dokumentenmanagementsystem (DMS) verwaltet rund 50 TB an aktuellen
und zur Archivierung vorgesehenen Daten. In der bestehenden Umgebung gibt es
einen proprietären Suchindex auf physischen Servern. Für den ersten Test
genügen synthetische Dokumente; die 50 TB sind weder ein Ziel für diesen
Aufbau noch ein Maß für die Größe des späteren Elasticsearch-Index.

Für die spätere Anbindung sind vor allem drei Dinge zu klären:

- Welche Rolle soll Elasticsearch gegenüber dem proprietären Suchindex
  übernehmen, und welches System übergibt die Daten zur Indexierung?
- Welche Inhalte und Metadaten müssen durchsuchbar sein, und welche
  Zugriffsrechte aus dem DMS müssen dabei gelten?
- Was passiert im Suchindex, wenn Dokumente geändert, gelöscht oder ins
  Archiv verschoben werden?

## Erster Meilenstein [erster-meilenstein]

```yaml block-meta
updated: "2026-11-20 12"
status: active
relations: []
```

Der lokale Testaufbau verwendet Elasticsearch 9.4.2 mit festem Image-Digest.
Er benötigt Docker mit Compose und für den Funktionstest Python 3. Der
Linux-Docker-Host braucht `vm.max_map_count` von mindestens `1048576`;
für den Container ist ein Speicherlimit von 2 GiB eingerichtet.
Der lokale Test verwendet absolute Speichergrenzen: Auf dem Dateisystem
des Docker-Datenvolumes sollten vor dem Start mindestens 3 GiB frei sein.
Unter 2 GiB greift die hohe Speichergrenze, unter 1 GiB kann Elasticsearch
Schreibzugriffe sperren. Diese Werte gelten nur für diesen kleinen Testaufbau.

Im Projektverzeichnis ausführen:

```shell
docker compose up -d --wait --wait-timeout 120
python3 scripts/test_elasticsearch.py
docker compose down
```

Elasticsearch läuft ohne Anmeldung nur im internen Docker-Testnetz.
Es gibt keinen veröffentlichten Host-Port; der Funktionstest greift über
`docker compose exec` zu. Er indexiert und sucht ein synthetisches
Dokument und entfernt den dabei erzeugten Index wieder. Das Datenvolume
bleibt nach `docker compose down` erhalten. DMS-Anbindung, Netzregeln der
Zielumgebung und Produktionslast sind nicht Teil dieses Tests.
