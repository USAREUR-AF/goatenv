<h1 align="center">goatenv</h1>

<p align="center">
  A complete example goat environment, kept separate from the code it deploys.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

> [!NOTE]
> goat is pre-1.0: interfaces can still change between releases. This repository is generated from goat's source tree; each update arrives as a new commit on `main`.

This is what a goat environment looks like when it is written down: one goatnet, `zagros`, as an overlay that uses [`goatcore`](https://github.com/usareur-af/goatcore) by pinned release. It is generated from the four invented facts in `goatlite.yaml`, and every value is an example. Copy it, change the facts and render your own.

## What an environment owns

| Path | Holds |
|---|---|
| `goatlite.yaml` | the four facts everything else is generated from |
| `goatcore.ref` | the `goatcore` release this environment is built with |
| `ops/ansible/group_vars/zagros_hosts/` | the site's declaration: zone, flags, each component's settings |
| `ops/ansible/inventory/` | the machines, and how a laptop reaches them |
| `ops/pins/` | which image digest each component runs here |
| `ops/enrollment/` | the certificate manifest, the CA's root certificate and public key |
| `terraform-zagros/` | an optional cloud footprint in your own AWS account: two relays with DNS, using goatcore's modules by tag |

Secrets are never in this repository. A laptop-only start uses `goatbuilder secrets init`, and larger teams declare their own store.

## What `zagros` covers

`zagros` is a LAN goatnet: `has_acme: false`, no relay addresses, and a private `zagros.lan` DNS zone served by the host's own CoreDNS. Peers enroll over the LAN.

An internet goatnet, with peers enrolling through relays, a public DNS zone and ACME certificates, needs more than this tree holds:

| Needs | Where it comes from |
|---|---|
| relays and their public DNS | `terraform-zagros/`, then `ops/ansible/inventory/generate-relays.sh` in `goatcore` |
| the mgmt host's tunnels to the relays (standup phase 5) | `goatcore`'s `ops/ansible/site-rathole-client.yml` |
| the site's OIDC clients (standup phase 10) | `goatcore`'s `ops/ansible/site-oidc-clients.yml` |
| a public zone, ACME and relay addresses in `group_vars` | written by hand; goatlite's renderer refuses `lite.internet` until growing out of lite is built ([goatlite design](https://github.com/usareur-af/goatcore/blob/main/docs/design/goatlite.md), sections 6 and 10) |

The two generic plays ship in `goatcore` releases after `goatcore/v0.1.0`; move `goatcore.ref` to one of those to use them.

The `ops/scripts/` tools are part of `goatcore`, not of an environment, which is why this tree has no `ops/scripts/`.

## Using it

This repository holds only what an environment owns. The tools live in `goatcore`, so copy this tree over a checkout of `goatcore` at the tag in `goatcore.ref` and work from there:

```bash
git clone --branch "$(cat goatcore.ref)" https://github.com/usareur-af/goatcore.git
cp -R ops goatlite.yaml goatcore/
cd goatcore && python3 ops/scripts/standup-config-preflight.py zagros_hosts
```

To make your own, change all four facts in `goatlite.yaml`, including the name, then follow [goatlite, the first goatnet](https://github.com/usareur-af/goatcore/blob/main/docs/tutorials/00-goatlite.md). The name `zagros` belongs to this example: its root certificate is here and its key is not, so a render under that name refuses with "half a CA exists". The walkthrough with recorded output to compare against is [`usareur-af/hello-galaxy-goatenv`](https://github.com/usareur-af/hello-galaxy-goatenv).

## Licence

`goatenv` was written by U.S. Federal government employees. In the U.S. it is not subject to copyright and is in the public domain; in countries where copyright is recognized, it is released under the [Apache License 2.0](LICENSE). See [INTENT.md](INTENT.md). [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md).
