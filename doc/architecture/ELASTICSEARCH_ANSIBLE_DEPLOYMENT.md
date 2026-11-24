---
title: Elasticsearch-Deployment mit Ansible
project: pie_ansible
agent_project: pie_ansible
scope: architecture
purpose: Beschreibt Ansible-Rollen, Plattformpakete und sichere Konfiguration für Elasticsearch und Kibana.
created: null
updated: "2026-11-24 13"
update_reason: "Paketverzeichnisse für Elasticsearch und Kibana dokumentiert."
status: draft
relations:
  - target: ../network/README.md
    type: reference
    reason: Beschreibt Elasticsearch-Zielhosts, Anwendungsgrenzen und Netzwerkkontext.
---

# Elasticsearch-Deployment mit Ansible

## Deployment-Umfang [deployment-umfang]

```yaml block-meta
updated: "2026-11-22 07"
status: active
relations:
  - target: ../network/README.md#elasticsearch-zielhosts
    type: reference
    reason: Das Netzwerkinventar führt Elasticsearch-Zielhosts nach Umgebung und Fachbereich auf.
```

Das Inventar gruppiert Elasticsearch-Hosts als
`elastic_<umgebung>_dept_<fachbereich>`. Jede Gruppe gehört zur Business-App
auf den entsprechenden eMain-Hosts derselben Umgebung und desselben
Fachbereichs. Eine Gruppe kann zunächst aus einem einzelnen Elasticsearch-
Host bestehen und später zu einem Cluster erweitert werden.

Elasticsearch und Kibana werden zunächst gemeinsam auf den Hosts der
jeweiligen `elastic`-Gruppe installiert. Das Playbook unterstützt Ubuntu
24 LTS und SUSE Linux Enterprise Server 15 (SLES 15); es wählt das
Paketformat anhand der Betriebssystem-Facts.

## Playbooks und Rollen [playbooks-und-rollen]

```yaml block-meta
updated: "2026-11-22 07"
status: active
relations: []
```

Playbooks bleiben schlank; wiederverwendbare Installations- und
Konfigurationslogik liegt in Rollen. Die implementierte Struktur ist:

```text
config/ansible/
  ansible.cfg
  group_vars/
    elastic/
      vars.yml
      vault.yml.example
  playbooks/
    elastic-stack.yml
  roles/
    common/
      defaults/main.yml
      tasks/main.yml
    elasticsearch/
      defaults/main.yml
      tasks/main.yml
      handlers/main.yml
      templates/
        elasticsearch.yml.j2
    kibana/
      defaults/main.yml
      tasks/main.yml
      handlers/main.yml
      templates/
        kibana.yml.j2
```

Die Rolle `common` enthält die gemeinsamen Defaults, die zuvor in
`config/ansible/main.yml` lagen. Sie prüft Paket- und Zertifikatsdateien,
bevor die Anwendungsrollen Änderungen an Zielhosts vornehmen. Die
Elasticsearch-Rolle installiert und konfiguriert Elasticsearch; danach
richtet die Kibana-Rolle die Weboberfläche und ihre Verbindung zum lokalen
Elasticsearch-Knoten ein. Das Playbook zielt auf die `elastic`-Gruppe und
verwendet Privilegienerweiterung.

## Pakete und Ausführung je Plattform [pakete-und-plattformen]

```yaml block-meta
updated: "2026-11-22 07"
status: active
relations: []
```

Die gemeinsamen Defaults setzen `ansible_master_location` auf
`/srv/Ansible_Sources` auf dem Ansible-Controller. Darunter erwartet Ansible
je ein Paket in den Verzeichnissen `elasticsearch/deb/`,
`elasticsearch/rpm/`, `kibana/deb/` und `kibana/rpm/`. Die Dateinamen
enthalten Version und Architektur, zum Beispiel:

```sh
elasticsearch-8.19.0-amd64.deb
elasticsearch-8.19.0-x86_64.rpm
kibana-8.19.0-amd64.deb
kibana-8.19.0-x86_64.rpm
```

Vor der Installation prüft Ansible, dass alle vier Pakete vorhanden und
korrekt benannt sind, ihre Dateinamen-Versionen übereinstimmen und
Elasticsearch sowie Kibana versionsgleich sind. Zusätzlich wird die
Paketmetadaten-Version des jeweils gewählten Pakets geprüft. Für Ubuntu
24 LTS wird das DEB mit `apt`, für SLES 15 das RPM mit `zypper` installiert.
Die Betriebssystem-Facts wählen den passenden Pfad, sodass beide Plattformen
mit einem Playbook-Aufruf bedient werden können. Paket-Signaturprüfungen
bleiben aktiv; SLES muss dem Paketsignaturschlüssel vertrauen und
Abhängigkeiten über konfigurierte Repositories beziehen können.

Der erste Rollout sollte eine einzelne Testgruppe ansteuern. Nach Prüfung
von Diensten und Netzwerkzugriff kann die Ausweitung auf weitere Umgebungs-
und Fachbereichsgruppen erfolgen.

Die Zugangsdaten werden vor dem Lauf vorbereitet und verschlüsselt:

```sh
cp config/ansible/group_vars/elastic/vault.yml.example \
  config/ansible/group_vars/elastic/vault.yml
ansible-vault encrypt config/ansible/group_vars/elastic/vault.yml
ANSIBLE_CONFIG=config/ansible/ansible.cfg \
  ansible-playbook config/ansible/playbooks/elastic-stack.yml \
  --limit elastic_qa_dept_a --ask-vault-pass
```

`elastic_qa_dept_a` ist ein Beispiel für den ersten Testlauf. Das Ziel muss
erreichbar sein und zu einer der unterstützten Plattformen gehören.

Die Verbindung erfolgt per SSH mit dem konfigurierten `serviceuser`
(`dummysvc` als Default) und Ansible-Privilegienerweiterung. Das Konto
benötigt nicht-interaktive `sudo`-Berechtigungen. Elasticsearch und Kibana
laufen unter ihren jeweiligen, vom Paket verwalteten Dienstkonten.

## Konfigurationsdefaults [konfigurationsdefaults]

```yaml block-meta
updated: "2026-11-22 07"
status: active
relations: []
```

Die gemeinsamen Defaults in
`config/ansible/roles/common/defaults/main.yml` enthalten
`serviceuser: dummysvc`,
`servicegroup: dummygroup`, `ansible_master_location:
/srv/Ansible_Sources` und `install_location: /srv`. Diese gemeinsamen Werte
gehören in `common/defaults/main.yml`; Elasticsearch-spezifische Werte
liegen in der Elasticsearch-Rolle oder in Inventarvariablen.

Als erste Elasticsearch-Defaults gelten:

| Einstellung | Default |
|---|---|
| Datenverzeichnis | `/srv/elasticsearch/data` |
| Elasticsearch-Konfiguration | `/etc/elasticsearch` |
| Kibana-Konfiguration | `/etc/kibana` |
| Elasticsearch-Dienst | `elasticsearch`, aktiviert und gestartet |
| Kibana-Dienst | `kibana`, aktiviert und gestartet |
| Clustername | `itdlz-<umgebung>-<fachbereich>` |
| Knotenname | Inventar-Hostname |
| Elasticsearch HTTP- und Transportports | `9200` und `9300` |
| Kibana HTTPS-Port | `5601` |
| Anfangstopologie | Ein Host je Umgebung und Fachbereich |
| Paketversion | Aus den gestagten Dateien gelesen; alle vier Pakete müssen übereinstimmen |

Der Paketbenutzer `elasticsearch` besitzt `/srv/elasticsearch/data`.
Konfigurations- und Logpfade bleiben bei den Paket- und
Betriebssystemdefaults. Kibana wird auf denselben Hosts installiert und
bindet seine HTTPS-Weboberfläche an die private IPv4-Adresse.

Für Gruppen mit nur einem Host wird Elasticsearch im Single-Node-Modus
konfiguriert. Wächst eine Gruppe zu einem Cluster, muss diese Einstellung
durch explizite Discovery- und Cluster-Bootstrap-Konfiguration ersetzt
werden.

## Sicherheit und Betrieb [sicherheit-und-betrieb]

```yaml block-meta
updated: "2026-11-22 07"
status: draft
relations:
  - target: ../network/README.md#offene-netzdetails
    type: reference
    reason: Erreichbarkeit über die Firewall und Anwendungszugriff müssen noch mit dem Netzwerk abgestimmt werden.
```

Elasticsearch bindet nur an die vorgesehene private Netzwerkschnittstelle.
Port `9200` ist nur von den passenden eMain-Anwendungshosts erreichbar;
Port `9300` ist auf Mitglieder desselben Elasticsearch-Clusters
beschränkt. Diese Regeln sind vor dem Deployment mit der tatsächlichen
Firewall-Konfiguration abzugleichen.

Elasticsearch-Sicherheit sowie TLS für HTTP und Transport werden
aktiviert. Auch Kibanas Weboberfläche und Verbindung zu Elasticsearch
verwenden TLS. Auf dem Ansible-Controller müssen je Inventar-Hostname diese
Dateien bereitliegen:

```text
/srv/Ansible_Sources/certificates/<inventory_hostname>/
  ca.crt
  elasticsearch.crt
  elasticsearch.key
  kibana.crt
  kibana.key
```

Das Elasticsearch-Zertifikat muss für den verwendeten Inventory-Hostnamen
gültig sein und Server- sowie Clientauthentifizierung für die
Transportverbindung erlauben. Das Kibana-Zertifikat muss für die Adresse
gültig sein, unter der Benutzer die Weboberfläche aufrufen. Die CA muss
beide Dienstzertifikate ausstellen oder ihnen vertrauen. Private Schlüssel
werden mit eingeschränkten Berechtigungen auf die Zielhosts kopiert.

`config/ansible/group_vars/elastic/vault.yml.example` ist nach
`config/ansible/group_vars/elastic/vault.yml` zu kopieren. Dort werden
starke, unterschiedliche Werte für `elasticsearch_bootstrap_password` und
`kibana_system_password` eingetragen und die Datei anschließend mit
`ansible-vault` verschlüsselt. Die verschlüsselte Datei sowie eine
Vault-Passwortdatei sind von Git ausgeschlossen. Zugangsdaten liegen nicht
im Inventory oder in Rollen-Defaults. Die Kibana-Konfiguration auf dem
Zielhost enthält das Kibana-Zugangspasswort und ist deshalb auf den
Dienstbenutzer beschränkt. Bei der Ersteinrichtung wird der Bootstrap-Wert
als Passwort des `elastic`-Benutzers gesetzt; anschließend wird
`bootstrap.password` aus dem Elasticsearch-Keystore entfernt.
Eine spätere Änderung des Passworts für den `elastic`-Benutzer muss mit
dem dazugehörigen Elasticsearch-Verfahren abgestimmt werden; das Playbook
verwendet den Vault-Wert für die API-Authentifizierung.

Die Rolle ist idempotent und überschreibt keine bestehenden Daten.
Backups, Aufbewahrungsfristen, JVM-Heap-Größe, Speicherlimits,
Zertifikatsausstellung und konkrete Firewall-Regeln sind vor einem
Produktions-Rollout noch festzulegen. Die Rollen ändern keine
Firewallregeln.
