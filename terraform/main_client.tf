resource "google_compute_instance" "windows-vm" {
  name         = "windows-vm"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "windows-cloud/windows-2019"
      labels = {
        my_label = "repaldo-project"
      }
    }
  }

  network_interface {
    network =  google_compute_network.vpc_network.self_link
    access_config {
    }
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    echo 'Installing Bacula client...'
    wget -O /tmp/bacula-client.exe https://sourceforge.net/projects/bacula/files/bacula/13.0.3/bacula-client-13.0.3-win64.exe/download
    /tmp/bacula-client.exe /S
    EOF
  allow_stopping_for_update = true

}

resource "google_compute_instance" "linux-vm1" {
  name         = "linux-vm1"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
      labels = {
        my_label = "repaldo-project"
      }
    }
  }

  network_interface {
    network =  google_compute_network.vpc_network.self_link
    access_config {
    }
  }

  
  metadata_startup_script = "sudo apt-get install -y bacula-client=13.0.3-1; dpkg -l | grep bacula-client"
  allow_stopping_for_update = true

}

resource "google_compute_instance" "linux-vm2" {
  name         = "linux-vm2"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
      labels = {
        my_label = "repaldo-project"
      }
    }
  }

  network_interface {
    network =  google_compute_network.vpc_network.self_link
    access_config {
    }
  }

  metadata_startup_script = "sudo apt-get install -y bacula-client=13.0.3-1; dpkg -l | grep bacula-client"
  allow_stopping_for_update = true

}

resource "google_compute_network" "vpc_network" {
  name                    = "terraform-network"
  auto_create_subnetworks = "true"
  
}

resource "google_compute_firewall" "ssh-rule" {
  name = "vm-instance"
  network = google_compute_network.vpc_network.name
  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = [ "22", "443" ]
  }

   source_ranges = [ "0.0.0.0/0" ]
   target_tags = ["vm-instance"]
}