---
project: pie_ansible
scope: guides
created: "2026-11-24 14"
updated: "2026-11-26 15"
update_reason: "Getrenntes Elasticsearch-Playbook und lokale Testzugangsdaten beschrieben."
status: draft
agent_project: pie_ansible
---

# Lokale Test-VM

Das `Vagrantfile` startet eine Ubuntu-24.04-VM mit KVM/libvirt. Es bindet
das Projektverzeichnis nicht in die VM ein und führt das Ansible-Playbook
nicht automatisch aus. Voraussetzung sind Vagrant, das Plugin
`vagrant-libvirt`, libvirt mit laufendem System-Socket, QEMU/KVM sowie
Ansible auf dem Entwicklungsrechner. Der Benutzer benötigt Zugriff auf
`/dev/kvm` und den libvirt-System-Socket.

Im Projektverzeichnis:

```sh
vagrant up --provider=libvirt
vagrant ssh-config > .vagrant/ssh_config
ANSIBLE_CONFIG=config/ansible/ansible.cfg \
  ansible -i config/ansible/inventory-vagrant.yml elastic -m ping
```

Die VM verwendet standardmäßig 2 GiB RAM und zwei CPUs. Das reicht zum
Erproben der VM-Verbindung, ist aber für Elasticsearch und Kibana knapp.
Bei ausreichend freiem Host-RAM kann vor dem ersten Start zum Beispiel
`ELASTIC_VM_MEMORY=4096 vagrant up --provider=libvirt` verwendet werden.
Nach Änderungen an der RAM-Vorgabe muss die VM mit derselben Vorgabe
neu geladen werden: `ELASTIC_VM_MEMORY=4096 vagrant reload`.

Das separate Inventar ordnet ausschließlich `elastic-vm` den Gruppen
`alf` und `elastic` zu und verwendet den
Vagrant-SSH-Zugang und `../Ansible_Sources` relativ zum Projektverzeichnis.
Die SSH-Konfiguration nach einem Neustart oder Neuaufbau der VM erneut
erzeugen. Die VM kann mit `vagrant halt` angehalten werden.

Für das Elasticsearch-Playbook müssen vorab die beiden Elasticsearch-Pakete
für Ubuntu und SLES, verschlüsselte Testzugangsdaten und Elasticsearch-
Testzertifikate bereitliegen. Das Zertifikatsverzeichnis heißt
`../Ansible_Sources/certificates/elastic-vm/`; das Elasticsearch-Zertifikat
muss die IPv4-Adresse der VM als Subject Alternative Name enthalten, da
Ansible für die API-Verbindung diese Adresse verwendet. Sie lässt sich mit
`vagrant ssh -c 'hostname -I'` ermitteln. Die bestehenden Anweisungen zu
Paketen und Vault stehen in
[Elasticsearch-Ansible-Deployment](../architecture/ELASTICSEARCH_ANSIBLE_DEPLOYMENT.md).

Nach Bereitstellung dieser Voraussetzungen wird ausschließlich Elasticsearch
mit dem lokalen Inventar installiert:

```sh
ANSIBLE_CONFIG=config/ansible/ansible.cfg \
  ansible-playbook -i config/ansible/inventory-vagrant.yml \
  config/ansible/playbooks/elasticsearch.yml --ask-vault-pass
```

`kibana.yml` installiert Kibana separat auf einem Ziel mit erreichbarem
Elasticsearch; `elastic-stack.yml` installiert beide Dienste nacheinander.

Für einen isolierten lokalen Test kann stattdessen ein Inventory unter
`config/ansible/.local/` verwendet werden, damit der vorhandene Elastic-Vault
nicht automatisch geladen wird. Die lokalen Testpasswörter können in einer
separaten Datei `config/ansible/.local/vm-test-vars.yml` liegen und mit
`-e @config/ansible/.local/vm-test-vars.yml` übergeben werden. Beide Dateien
sind Git-ignoriert; die Passwortdatei muss auf den Benutzer beschränkt sein
(`chmod 600`). Unverschlüsselte Zugangsdaten sind ausschließlich für die
isolierte Test-VM vorgesehen, nicht für Produktionssysteme.
