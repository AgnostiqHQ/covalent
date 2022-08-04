# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

packer {
  required_plugins {
    amazon = {
      version = ">= 1.1.2"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "ami_name" {
  type    = string
  default = "covalent-linux"
}

variable "sha_tag" {
  type    = string
  default = ""
}

locals {
  ami_name     = var.sha_tag == "" ? var.ami_name : join("-", [var.ami_name, var.sha_tag])
  covalent_pip = var.sha_tag == "" ? "--pre covalent" : "git+https://github.com/AgnostiqHQ/covalent.git@${var.sha_tag}"
}

source "amazon-ebs" "ubuntu" {
  ami_name      = local.ami_name
  instance_type = "t2.micro"
  region        = "us-east-1"

  source_ami_filter {
    filters = {
      name                = "ubuntu-minimal/images/hvm-ssd/ubuntu-focal-20.04-amd64-minimal-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }

    most_recent = true
    owners      = ["099720109477"]
  }

  ssh_username = "ubuntu"

  tags = {
    OS_Version    = "Ubuntu 20.04"
    Release       = "${var.sha_tag == "" ? "latest" : var.sha_tag}"
    Base_AMI_Name = "{{ .SourceAMIName }}"
    Extra         = "{{ .SourceAMITags.TagName }}"
  }
}

build {
  name = "covalent"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y -f python3-pip",
      "sudo apt-get install -y rsync git",
      "sudo pip3 install --ignore-installed ${local.covalent_pip}"
    ]
  }
}
