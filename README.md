<h1 align="center">goatenv</h1>

<p align="center">
  A complete example goat environment, kept separate from the code it deploys.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

> [!NOTE]
> goat is pre-1.0: interfaces can still change between releases. This repository is generated from goat's source tree; each update arrives as a new commit on `main`.

This is what a goat environment looks like when it is written down: an overlay that uses [`goatcore`](https://github.com/usareur-af/goatcore) by pinned release. It holds two examples, each generated from invented facts in its own `goatlite.yaml`, and every value is an example:

| Example | Where | What it is |
|---|---|---|
| `zagros` | the repository root | a LAN goatnet: one box, peers enrol over the LAN |
| `example-internet` | [`internet/`](internet/) | the same preset grown to the internet: peers enrol from anywhere through relays, under a public zone with ACME certificates |

Copy one, change the facts and render your own.

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
| `internet/` | the internet example: the same paths for `example-internet`, plus `terraform-example-internet/` |
| `base-images-private-catalogue/` | an example of base images chosen by the environment: one file per role, from a private Chainguard catalogue |

Secrets are never in this repository. A laptop-only start uses `goatbuilder secrets init`, and larger teams declare their own store.

## Your own base images

Every goat image starts from base images named by role (`rust-build`, `go-build`, `node-build`, `runtime-cc`, `runtime-static`, `runtime-shell`). The public images `zagros` pins are built on goatcore's defaults: Chainguard's free images, pinned by digest. An environment that wants other bases, such as a private Chainguard catalogue or its own mirror, carries a file per role at `ops/base-images/<role>/Dockerfile`, holding one digest-pinned `FROM` line. When the environment is copied over goatcore, those files replace the defaults, and every image built from that tree uses them. No Dockerfile changes.

[`base-images-private-catalogue/`](base-images-private-catalogue/) holds six such files for a private catalogue under a placeholder organisation, `example-org`:

```text
base-images-private-catalogue/ops/base-images/rust-build/Dockerfile   FROM cgr.dev/example-org/rust:1.92-dev@sha256:<digest>
base-images-private-catalogue/ops/base-images/runtime-cc/Dockerfile   FROM cgr.dev/example-org/glibc-dynamic-fips:latest@sha256:<digest>
…
```

To build on them, copy them into this tree's `ops/`, assemble as below, build and pin your own digests:

```bash
cp -R base-images-private-catalogue/ops .       # the environment now chooses its bases
docker login cgr.dev                            # a private catalogue needs your pull credentials
git clone --branch "$(cat goatcore.ref)" https://github.com/usareur-af/goatcore.git
cp -R ops goatlite.yaml goatcore/
cd goatcore
python3 ops/base-images/base-images.py list     # your images for every role
python3 ops/base-images/base-images.py build --unit goat-relay-image \
  --tag registry.example.org/zagros/goat-relay:local-1 --platform linux/amd64,linux/arm64 --push
```

Then put the pushed digest in `ops/pins/fleet-pins.yaml` in place of the public image. Refresh the role digests with Dependabot on the `ops/base-images/<role>` directories, or with `crane digest`. The procedure and the rules each role's image must meet: goatcore's [build goat images on your own base images](https://github.com/usareur-af/goatcore/blob/main/docs/operations/build-on-your-own-base-images.md). The rehearsed walkthrough: [`usareur-af/hello-galaxy-goatenv`](https://github.com/usareur-af/hello-galaxy-goatenv) `base-images/`.

## What `zagros` covers

`zagros` is a LAN goatnet: `has_acme: false`, no relay addresses, and a private `zagros.lan` DNS zone served by the host's own CoreDNS. Peers enroll over the LAN.

## The internet example, `example-internet`

> [!WARNING]
> Status: WIP, not for production use — gate: one internet standup from the rendered example on real relays.

[`internet/`](internet/) is a whole second overlay. Its `goatlite.yaml` is the four facts plus a `lite.internet:` block, and the renderer produced everything else from it:

```yaml
lite:
  name: example-internet
  host: 192.0.2.20
  ssh_user: ubuntu
  admin: admin@example.org
  internet:
    zone: goatnet.example        # a public zone whose DNS Cloudflare serves
```

The block also takes `acme_email` (default `admin`), `aws_profile` (default the name), `relays` (default two, `a` and `b`), `cloudflare_token_ref` and, after standup phase 8 enrols the box, `mesh_ip`. A LAN goatlite grows into this shape by adding the block and rendering again; the SPIRE trust domain and the CA stay as they were.

| What the block changes | Where it is |
|---|---|
| ACME certificates through Cloudflare DNS-01 (`has_acme: true`, `dashboard_cert_delivery_mode: acme`, `acme_email`) | `internet/ops/ansible/group_vars/example_internet_hosts/vars.yml` |
| the public enrolment apex `netbird.goatnet.example`, which is also `site_dns_zone` | the same file, and `signal_uri` in `internet/ops/ansible/inventory/mgmt-hosts.ini` |
| the relays: `relay_addresses` (`rels://…:33073`), `stun_hosts`, the AWS profile | the same file |
| the Cloudflare token: a lookup of `CLOUDFLARE_API_TOKEN_EXAMPLE_INTERNET` under your secrets store, never a value | the same file |
| two relays, their public names, the apex round-robin and the SSM bucket | `internet/terraform-example-internet/main.tf` |
| the relays' TLS posture, `le-dns01` | `internet/ops/ansible/inventory/relay-tls-posture.sh` |
| the router certificate under the public apex, no LAN certificates | `internet/ops/enrollment/manifests/example-internet-certs.yaml` |

`goatbuilder standup example-internet` then runs the internet profile: the relay tunnels in phase 5, ACME and the relay tier in phase 7, the mesh enrolment in phase 8, the OIDC clients in phase 10. The plays it reaches ship in `goatcore` releases after `goatcore/v0.1.0`; move `goatcore.ref` to one of those to use them.

The `ops/scripts/` tools are part of `goatcore`, not of an environment, which is why this tree has no `ops/scripts/`.

## Using it

This repository holds only what an environment owns. The tools live in `goatcore`, so copy this tree over a checkout of `goatcore` at the tag in `goatcore.ref` and work from there:

```bash
git clone --branch "$(cat goatcore.ref)" https://github.com/usareur-af/goatcore.git
cp -R ops goatlite.yaml goatcore/
cd goatcore && python3 ops/scripts/standup-config-preflight.py zagros_hosts
```

The internet example goes over its own checkout the same way, from `internet/`:

```bash
cp -R internet/ops internet/goatlite.yaml internet/terraform-example-internet goatcore/
cd goatcore && python3 ops/scripts/goatlite-render.py --site example-internet --verify
```

`--verify` checks that the rendered values are the internet ones: ACME on, the public apex as the zone, the relays' addresses, mesh-only routes, and every secret a lookup under your store.

To make your own, change all four facts in `goatlite.yaml`, including the name, then follow [goatlite, the first goatnet](https://github.com/usareur-af/goatcore/blob/main/docs/tutorials/00-goatlite.md). The names `zagros` and `example-internet` belong to these examples: their root certificates are here and their keys are not, so a render under either name refuses with "half a CA exists". The walkthrough with recorded output to compare against is [`usareur-af/hello-galaxy-goatenv`](https://github.com/usareur-af/hello-galaxy-goatenv).

## Licence

`goatenv` was written by U.S. Federal government employees. In the U.S. it is not subject to copyright and is in the public domain; in countries where copyright is recognized, it is released under the [Apache License 2.0](LICENSE). See [INTENT.md](INTENT.md). [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md).
