provider "google" {
  // credentials = "$(file(vistoq-demo-0faef097b7b7.json"
  project = "vistoq-demo"
  region = "us-central1-b"
}

terraform {
  backend "gcs" {
    bucket = "tf-state-vistoq"
    prefix = "terraform/state"
  }
}

//variable "sshkey" {}
variable "sshkeypub" {}

resource "google_compute_firewall" "default" {
  name = "vistoq-firewall"
  network = "default"

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports = [
      "80",
      "8080",
      "443",
      "3978"
    ]
  }
}

resource "google_compute_address" "panorana_ext" {
  name = "panorana-int"
  region = "us-east4"

  provisioner "local-exec" {
    command = "echo ${google_compute_address.panorana_ext.address} > /var/tmp/vistoq_panorama_ip.txt"
  }
}

resource "google_compute_instance" "panorama" {
  name = "panorama-813"
  // machine_type = "custom-4-16384"
  // n1-highmem-4 == 4 vcpu and 26GB of RAM
  machine_type = "n1-highmem-4"
  zone = "us-east4-b"

  timeouts {
    create = "30m"
    delete = "30m"
  }

  tags = [
    "http",
    "https"]

  boot_disk {
    initialize_params {
      image = "panoram-813"
    }
  }

  can_ip_forward = true

  network_interface {
    network = "default"

    access_config {
      nat_ip = "${google_compute_address.panorana_ext.address}"
    }

  }

  metadata {
    block-projet-ssh-keys = true
    sshKeys = "admin:${var.sshkeypub}"
  }

  service_account {
    scopes = [
      "cloud-platform"
    ]
  }
}

resource "google_compute_instance" "controller" {
  name = "controller-01"
  machine_type = "n1-standard-2"
  zone = "us-central1-b"

  timeouts {
    create = "30m"
    delete = "30m"
  }

  tags = [
    "http"]

  boot_disk {
    initialize_params {
      // image = "ubuntu-1604-lts"
      image = "vistoq-controller-v01"
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral IP
    }

  }

  metadata_startup_script = "echo '${google_compute_address.panorana_ext.address} panorama' >> /etc/hosts"

  service_account {
    scopes = [
      "userinfo-email",
      "compute-ro",
      "storage-ro"]
  }

  depends_on = [
    "google_compute_address.panorana_ext"
  ]
}

resource "null_resource" "delay" {
  provisioner "local-exec" {
    command = "sleep 20"
  }
  triggers = {
    "before" = "${google_compute_instance.controller.id}"
  }
}

resource "google_compute_instance" "compute" {
  name = "compute-01"
  machine_type = "n1-standard-4"
  zone = "us-central1-b"

  timeouts {
    create = "30m"
    delete = "30m"
  }

  tags = [
    "http"
  ]

  boot_disk {
    initialize_params {
      // image = "ubuntu-1604-lts"
      image = "vistoq-compute-v01"
      type = "pd-ssd"
      size = "10"
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral IP
    }

  }

  metadata_startup_script = "echo $(hostname -f) > /etc/salt/minion_id"

  service_account {
    scopes = [
      "userinfo-email",
      "compute-ro",
      "storage-ro"
    ]
  }

  depends_on = [
    "null_resource.delay"
  ]
}







