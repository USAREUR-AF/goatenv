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
