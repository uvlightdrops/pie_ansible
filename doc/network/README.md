---
project: pie_ansible
scope: architecture
created: null
updated: "2026-11-22 07"
update_reason: "Netzwerkdokumentation um die gemeinsame Kibana-Bereitstellung mit Elasticsearch ergänzt."
status: draft
relations:
  - target: ../architecture/ELASTICSEARCH_ANSIBLE_DEPLOYMENT.md
    type: reference
    reason: Beschreibt den Ansible-Deployment-Ansatz für die hier aufgeführten Elasticsearch-Hosts.
---

# Netzwerk der Simulation

## Fachbereiche und Umgebungen [fachbereiche-und-umgebungen]

```yaml block-meta
updated: "2026-11-22 07"
status: active
relations: []
```

Hosts verschiedener Fachbereiche (`dept_a`, `dept_b` und `dept_c`) können
nicht miteinander kommunizieren. Diese Trennung gilt auch,
wenn zwei Hosts dieselbe Anwendung bedienen oder zur gleichen Umgebung
gehören. Die Zugehörigkeit zum selben Fachbereich bedeutet umgekehrt nicht,
dass jede Verbindung innerhalb dieses Fachbereichs erlaubt ist.

Das [Simulationsinventar](../../config/ansible/ans-inv-sim2.yml) gruppiert
die Hosts nach Anwendung, Umgebung und Fachbereich. Die Anwendungen heißen
`eMain` und `elastic`; die Umgebungen sind `live` (Produktion), `stage`
(Vorproduktion), `qa` (Test) und `train` (Schulung). `elastic_qa_dept_a`
ist beispielsweise die Hostgruppe für Elasticsearch in der Testumgebung
von `dept_a`.

## Elasticsearch-Zielhosts [elasticsearch-zielhosts]

```yaml block-meta
updated: "2026-11-22 07"
status: active
relations:
  - target: ../architecture/ELASTICSEARCH_ANSIBLE_DEPLOYMENT.md#deployment-umfang
    type: reference
    reason: Beschreibt den Ansible-Deployment-Umfang für diese Elasticsearch-Zielhosts.
```

Auf jedem Host einer `elastic_<umgebung>_dept_<kennung>`-Gruppe ist genau
ein Elasticsearch-Knoten vorgesehen. Kibana wird zunächst auf denselben
Hosts installiert und stellt die Weboberfläche per HTTPS auf Port `5601`
bereit. Die vorgesehenen Zielplattformen sind Ubuntu 24 LTS und SUSE Linux
Enterprise Server 15 (SLES 15). Die Zielhosts mit dem Namenspräfix
`srv-vm-` sind virtuelle Maschinen. Die Tabelle verwendet die Kurznamen
aus dem Inventar.

| Umgebung | `dept_a` | `dept_b` | `dept_c` |
|---|---|---|---|
| `live` | `srv-vm-501` | `srv-vm-502` | `srv-vm-503` |
| `stage` | `srv-vm-510` | `srv-vm-511` | `srv-vm-512` |
| `qa` | `srv-vm-610` | `srv-vm-611` | `srv-vm-612` |
| `train` | `srv-vm-710` | `srv-vm-711` | Gruppe ohne Hosts |

Die Gruppe `elastic_train_dept_c` ist vorhanden, enthält aber keine Hosts.
Das [Ansible-Deployment](../architecture/ELASTICSEARCH_ANSIBLE_DEPLOYMENT.md)
beschreibt die Installation von Elasticsearch und Kibana sowie die
Konfiguration der TLS-Verbindungen.

## Offene Netzdetails [offene-netzdetails]

```yaml block-meta
updated: "2026-11-22 07"
status: draft
relations:
  - target: ../architecture/ELASTICSEARCH_ANSIBLE_DEPLOYMENT.md#sicherheit-und-betrieb
    type: reference
    reason: Beschreibt die TLS-Konfiguration und setzt die offenen Firewallregeln voraus.
```

Elasticsearch-Knoten aus unterschiedlichen Fachbereichen können wegen der
Netztrennung keinen gemeinsamen Cluster bilden. Noch offen sind die
konkreten Netzabschnitte, Schnittstellen und erlaubten Verbindungen
innerhalb eines Fachbereichs. Zu klären sind insbesondere der Zugriff der
Business-App auf Elasticsearch-Port `9200`, der Browserzugriff auf
Kibana-Port `5601` und die Kommunikation zwischen Elasticsearch-Knoten über
Port `9300`. Auch die Cluster-Zuordnung innerhalb eines Fachbereichs ist
damit noch nicht festgelegt. Das Ansible-Deployment konfiguriert keine
Firewallregeln.
