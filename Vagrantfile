Vagrant.configure("2") do |config|
  config.vm.box = "cloud-image/ubuntu-24.04"
  config.vm.define "elastic-vm"
  config.vm.hostname = "elastic-vm"
  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.provider :libvirt do |libvirt|
    libvirt.memory = Integer(ENV.fetch("ELASTIC_VM_MEMORY", "2048"))
    libvirt.cpus = 2
  end
end
