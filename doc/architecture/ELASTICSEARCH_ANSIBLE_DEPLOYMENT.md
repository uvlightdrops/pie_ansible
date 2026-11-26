---
project: pie_ansible
agent_project: pie_ansible
scope: architecture
created: null
updated: "2026-11-26 18"
update_reason: "Temporäre Elasticsearch-Testzertifikate dokumentiert."
status: draft
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

Elasticsearch und Kibana können gemeinsam oder getrennt auf den Hosts der
jeweiligen `elastic`-Gruppe installiert werden. Die Playbooks unterstützen Ubuntu
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
  ans-inv-sim2.yml
  group_vars/
    elastic/
      vars.yml
      serviceuser.yml.example
      vault.yml.example
  playbooks/
    elastic-stack.yml
    elasticsearch.yml
    kibana.yml
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
Elasticsearch-Rolle installiert und konfiguriert Elasticsearch. Das separate
`elasticsearch.yml` führt nur diese Rolle aus; `kibana.yml` richtet Kibana
auf einem Ziel mit erreichbarem Elasticsearch ein. `elastic-stack.yml`
führt beide Rollen nacheinander aus. Alle drei Playbooks zielen auf `alf`
und verwendet Privilegienerweiterung. Die Gruppe `alf` muss im verwendeten
Inventory eingerichtet werden; im Simulationsinventar ist sie noch nicht
enthalten. Die ausgewählten Hosts müssen außerdem zur
Gruppe `elastic` gehören, damit sie deren Gruppenvariablen erhalten.

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

Vor der Installation prüft Ansible je Zielhost und ausgewähltem Dienst
ausschließlich das zu dessen Plattform passende Paket: DEB für Ubuntu,
RPM für SLES. Das jeweilige Verzeichnis muss genau ein passend benanntes
Paket enthalten. Beim gemeinsamen Deployment müssen die Versionen von
Elasticsearch und Kibana übereinstimmen. Das Kibana-Deployment prüft zusätzlich die Version des
erreichbaren Elasticsearch-Knotens. Zusätzlich wird die
Paketmetadaten-Version des jeweils gewählten Pakets geprüft. Für Ubuntu
24 LTS wird das DEB mit `apt`, für SLES 15 das RPM mit `zypper` installiert.
Die Betriebssystem-Facts wählen den passenden Pfad, sodass beide Plattformen
mit einem Playbook-Aufruf bedient werden können. Paket-Signaturprüfungen
bleiben aktiv; SLES muss dem Paketsignaturschlüssel vertrauen und
Abhängigkeiten über konfigurierte Repositories beziehen können.

Der erste Rollout sollte eine einzelne Testgruppe ansteuern. Nach Prüfung
von Diensten und Netzwerkzugriff kann die Ausweitung auf weitere Umgebungs-
und Fachbereichsgruppen erfolgen.

Das Standard-Inventory wird auf jedem Ansible-Controller lokal ausgewählt.
Für die Entwicklung kann das eingecheckte Simulationsinventar als Vorlage
verwendet werden:

```sh
mkdir -p config/ansible/.local
cp config/ansible/ans-inv-sim2.yml config/ansible/.local/inventory-dev.yml
chmod 600 config/ansible/.local/inventory-dev.yml
ln -s .local/inventory-dev.yml config/ansible/inventory.yml
```

In der lokalen Kopie `alf` als Gruppe mit `elastic` als Untergruppe
eintragen, damit das Playbook die Elastic-Hosts auswählt.

Auf dem Produktions-Controller das dortige Inventory als
`.local/inventory-prod.yml` bereitstellen und `inventory.yml` darauf
verlinken. Der Symlink und `.local/` sind von Git ausgeschlossen; sie
müssen nach einem neuen Checkout lokal eingerichtet werden.
`ansible.cfg` verwendet den Symlink als Standard. Ein explizites `-i`
überschreibt diese Auswahl, wie beim lokalen Vagrant-Inventar.
Der Symlink verschlüsselt das Inventory nicht.

Der Servicebenutzer wird auf dem Ansible-Controller lokal konfiguriert:

```sh
mkdir -p config/ansible/group_vars/elastic/.local
cp config/ansible/group_vars/elastic/serviceuser.yml.example \
  config/ansible/group_vars/elastic/.local/serviceuser-dev.yml
chmod 600 config/ansible/group_vars/elastic/.local/serviceuser-dev.yml
ln -s .local/serviceuser-dev.yml config/ansible/group_vars/elastic/serviceuser.yml
```

In `serviceuser-dev.yml` den Platzhalter durch den lokalen Servicebenutzer
ersetzen. Auf dem Produktions-Controller entsprechend `serviceuser-prod.yml`
in `.local/` anlegen und `serviceuser.yml` darauf verlinken. Der Symlink
und `.local/` sind von Git ausgeschlossen. Das versteckte Unterverzeichnis
verhindert, dass Ansible beide umgebungsspezifischen Dateien direkt lädt.
Die Auswahl gilt für alle Elastic-Ziele dieses Controllers; der Symlink
verschlüsselt keine Daten. Ohne lokale Einstellung bleibt der gemeinsame
Default `dummysvc` wirksam. Diese Variable bestimmt nicht den SSH-Benutzer.

Die Zugangsdaten werden vor dem Lauf vorbereitet und verschlüsselt:

```sh
cp config/ansible/group_vars/elastic/vault.yml.example \
  config/ansible/group_vars/elastic/.local/vault-dev.yml
chmod 600 config/ansible/group_vars/elastic/.local/vault-dev.yml
# Platzhalter in .local/vault-dev.yml durch Zugangsdaten ersetzen.
ansible-vault encrypt config/ansible/group_vars/elastic/.local/vault-dev.yml
ln -s .local/vault-dev.yml config/ansible/group_vars/elastic/vault.yml
ANSIBLE_CONFIG=config/ansible/ansible.cfg \
  ansible-playbook config/ansible/playbooks/elastic-stack.yml \
  --limit elastic_qa_dept_a --ask-vault-pass
```

Für Elasticsearch allein statt `elastic-stack.yml` das Playbook
`elasticsearch.yml` verwenden; es benötigt nur
`elasticsearch_bootstrap_password` und keine Kibana-Pakete oder
Kibana-Zertifikate. Für `kibana.yml` muss Elasticsearch bereits erreichbar
sein; zusätzlich zum Elasticsearch-Passwort wird
`kibana_system_password` benötigt. Das Kibana-Playbook setzt dieses
Passwort für das Elasticsearch-Konto `kibana_system`.

`elastic_qa_dept_a` ist ein Beispiel für den ersten Testlauf. Das Ziel muss
erreichbar sein und zu einer der unterstützten Plattformen gehören.

Die Verbindung erfolgt per SSH mit dem im Inventory konfigurierten
`ansible_user` und Ansible-Privilegienerweiterung. Ohne `ansible_user` gilt
die normale Ansible-Verbindungskonfiguration. Das SSH-Konto
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
| Paketversion | Aus dem jeweiligen Plattformpaket gelesen; Elasticsearch und Kibana müssen übereinstimmen |

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

Für einen befristeten Test können auf dem Ansible-Controller eine eigene
Test-CA und je Elasticsearch-Host ein eigenes Schlüsselpaar erstellt
werden. OpenSSL und Python 3 müssen installiert sein. Das Verzeichnis muss
außerhalb des Git-Repositories liegen:

```sh
python3 scripts/elasticsearch_test_certificates.py \
  --base-dir /srv/Ansible_Sources/certificates init-ca

python3 scripts/elasticsearch_test_certificates.py \
  --base-dir /srv/Ansible_Sources/certificates issue \
  --host elastic-beispiel.example.org \
  --san DNS:elastic-beispiel.example.org --san IP:192.0.2.10
```

`init-ca` wird einmal ausgeführt, `issue` für jeden Inventory-Host. Den
Hostnamen und alle tatsächlich verwendeten DNS-Namen beziehungsweise
IP-Adressen als SAN angeben; es werden keine Adressen automatisch ermittelt.
Die CA gilt 30 Tage, die Hostzertifikate sieben Tage. Ein existierendes
Hostverzeichnis darf verwendet werden, vorhandene Ausgabedateien oder eine
vorhandene CA werden nicht überschrieben. Das Skript erzeugt nur die
Elasticsearch-Dateien, keine Kibana-Zertifikate.

Die Test-CA und die unverschlüsselten privaten Schlüssel sind vertraulich.
Der CA-Schlüssel bleibt auf dem Controller; Clients müssen der Test-CA
vertrauen. Für regulären Betrieb die Testzertifikate rechtzeitig durch die
offiziellen PKI-Zertifikate ersetzen und auch das Vertrauen der Clients
umstellen. Die CA nicht wiederverwenden, wenn ihr Schlüssel kompromittiert
wurde.

`config/ansible/group_vars/elastic/vault.yml.example` wird wie oben
beschrieben lokal kopiert. Dort werden
starke, unterschiedliche Werte für `elasticsearch_bootstrap_password` und
`kibana_system_password` eingetragen und die Datei anschließend mit
`ansible-vault` verschlüsselt und als `vault.yml` verlinkt. Auf dem
Produktions-Controller wird entsprechend eine lokale `vault-prod.yml`
verwendet. Die verschlüsselte Datei, der Symlink sowie eine
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
