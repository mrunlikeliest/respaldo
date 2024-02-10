terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.1.0"
    }
  }
}
provider "google" {
    credentials = file("./respaldo-wannacry-9411fdf3d12d.json")
    project     = "respaldo-wannacry"
    region      = "us-east1"
    zone        = "us-east1-b"
}

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

# VPC Creation
resource "google_compute_network" "vpc" {
    name                    = "bacula-network"
    auto_create_subnetworks = "false"
}

# Subnet Creation
resource "google_compute_subnetwork" "subnet" {
    name          = "my-subnet"
    region        = "us-east1"
    network       = google_compute_network.vpc.name
    ip_cidr_range = "10.0.0.0/16"
}

# VM Instance for Bacula
resource "google_compute_instance" "instance_1" {
    name         = "bacula-instance"
    machine_type = "n1-standard-1"
    zone         = "us-east1-b"
    tags         = ["bacula", "instance-1"]

    boot_disk {
        initialize_params {
        image = "debian-cloud/debian-10"
        }
    }

    network_interface {
        subnetwork = google_compute_subnetwork.subnet.name
        access_config {
        }
    }

    metadata_startup_script = <<SCRIPT
        sudo apt update
       # sudo apt install -y bacula-director bacula-storage bacula-console
        # Add additional configurations or packages as needed

    SCRIPT
}

# Google SQL Database Instance
resource "google_sql_database_instance" "sql_instance" {
    name = "bacula-sql"
    database_version = "POSTGRES_15"
    region = "us-east1"
    deletion_protection = false
    settings {
        tier = "db-f1-micro"
        availability_type = "REGIONAL"
    }
}

resource "google_sql_database" "sql_database" {
  name              = "sql_db"
  instance          = google_sql_database_instance.sql_instance.name
  charset           = "UTF8"
  collation         = "en_US.UTF8"
}

// Enabling interoperability and storing keys

#Creating a service account
resource "google_service_account" "interop" {
  account_id = "interop-account"
}

#Creating storage
resource "google_storage_bucket" "bucket_1" {
  name          = "bacula-storage"
  location      = "US"
  storage_class = "STANDARD"
  uniform_bucket_level_access = true
}

# Grant Storage Admin role to the interop-account service account
resource "google_project_iam_member" "interop_iam_binding" {
  project = "respaldo-wannacry"
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.interop.email}"
}

resource "google_storage_hmac_key" "interop" {
  service_account_email = google_service_account.interop.email
}

output "access_key" {
  value = google_storage_hmac_key.interop.access_id
}

output "secret_key" {
  value     = google_storage_hmac_key.interop.secret
   sensitive = true
}

# Define a variable for the database name
variable "database_name" {
  description = "Name of the Google SQL database instance"
  type        = string
  default     = "bacula-sql"  # Set the default value to your database name
}

# Define a variable for the bucket name
variable "bucket_name" {
  description = "Name of the Google Cloud Storage bucket"
  type        = string
  default     = "bacula-storage"  # Set the default value to your bucket name
}



# ... (other resource definitions)

# Output the database name
output "database_name" {
  value = var.database_name
}

# Output the bucket name
output "bucket_name" {
  value = var.bucket_name
}

# Firewall Rule for Bacula
resource "google_compute_firewall" "bacula-firewall" {
  name    = "allow-bacula"
  network = google_compute_network.vpc.name
     allow {
    protocol = "icmp"
  }

  allow {
    protocol = "TCP"
    ports    = ["22","443"]
  }
  source_ranges = ["0.0.0.0/0"]  // Adjust as necessary for security requirements
  target_tags   = ["bacula"]
}

