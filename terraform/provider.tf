terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.1.0"
    }
  }
}

provider "google" {
  project = "respaldo-wannacry"
  region = "us-central1"
  zone = "us-central1-a"
  credentials = "./respaldo-keys.json"
}