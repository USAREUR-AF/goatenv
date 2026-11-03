# The cloud footprint of the example goatnet `zagros`: two relays in your own AWS
# account, with DNS through Cloudflare. A LAN-only goatnet needs none of this.
#
#   cd terraform-zagros
#   terraform init            # add a backend first if more than one person applies it
#   terraform apply -var aws_account_id=... -var cloudflare_zone_id=...
#
# ops/ansible/inventory/generate-relays.sh reads the `relays` output below, so
# `goatbuilder standup` finds the relays with no further wiring.

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

variable "aws_account_id" {
  description = "Your AWS account. Terraform refuses to apply with credentials for any other account."
  type        = string
}

variable "cloudflare_zone_id" {
  description = "The Cloudflare zone id of your goatnet's public domain."
  type        = string
}

variable "cloudflare_zone_name" {
  description = "Your goatnet's public domain."
  type        = string
  default     = "zagros.example"
}

# One aws provider per relay region: Terraform cannot pass a provider to a for_each'd module.
provider "aws" {
  alias               = "a"
  region              = "us-east-2"
  allowed_account_ids = [var.aws_account_id]
}

provider "aws" {
  alias               = "b"
  region              = "eu-west-1"
  allowed_account_ids = [var.aws_account_id]
}

provider "cloudflare" {} # reads CLOUDFLARE_API_TOKEN

module "relay_a" {
  source    = "git::https://github.com/usareur-af/goatcore.git//terraform/modules/goat-relay?ref=goatcore/v0.1.0"
  providers = { aws = aws.a }

  relay_name           = "a"
  region               = "us-east-2"
  project              = "goat"
  environment          = "zagros"
  cloudflare_zone_id   = var.cloudflare_zone_id
  cloudflare_zone_name = var.cloudflare_zone_name
}

module "relay_b" {
  source    = "git::https://github.com/usareur-af/goatcore.git//terraform/modules/goat-relay?ref=goatcore/v0.1.0"
  providers = { aws = aws.b }

  relay_name           = "b"
  region               = "eu-west-1"
  project              = "goat"
  environment          = "zagros"
  cloudflare_zone_id   = var.cloudflare_zone_id
  cloudflare_zone_name = var.cloudflare_zone_name
}

output "relays" {
  value = {
    a = {
      public_ip           = module.relay_a.public_ip
      instance_id         = module.relay_a.instance_id
      region              = "us-east-2"
      relay_url           = module.relay_a.relay_url
      ssh_key_secret_name = module.relay_a.ssh_key_secret_name
      rathole_secret_name = module.relay_a.rathole_secret_name
    }
    b = {
      public_ip           = module.relay_b.public_ip
      instance_id         = module.relay_b.instance_id
      region              = "eu-west-1"
      relay_url           = module.relay_b.relay_url
      ssh_key_secret_name = module.relay_b.ssh_key_secret_name
      rathole_secret_name = module.relay_b.rathole_secret_name
    }
  }
}
