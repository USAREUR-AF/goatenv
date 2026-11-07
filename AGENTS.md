# AGENTS.md

Instructions for AI coding agents, and a short version for anyone working here. [CONTRIBUTING.md](CONTRIBUTING.md) is the full process.

## What this repository is

goatenv is a complete example goat environment, written down: an overlay for goatcore that defines one synthetic goatnet, `zagros`, with every file a real deployment's overlay carries (inventories, group_vars, pins, warrants, Terraform roots). Copy its shape for a new environment; never put a real environment's values here.

It sits beside [goatcore](https://github.com/usareur-af/goatcore), which builds and runs a goatnet. A real deployment is goatcore at a pinned commit plus a private overlay repository with that deployment's configuration; no deployment's configuration is ever in this repository.

## Layout

| Path | What |
|---|---|
| `goatcore.ref` | the goatcore commit this environment builds with; bump it in its own pull request |
| `goatlite.yaml` | the four facts the single-box files are generated from |
| `ops/ansible/` | inventories and `group_vars/zagros_*` |
| `ops/pins/`, `ops/warrant/`, `ops/goatnets/` | image pins, mesh access warrants, the goatnet registry |
| `terraform-zagros/` | the environment's Terraform root, calling goatcore's modules |
| `internet/` | the same environment reachable from the internet |

## Rules CI enforces

1. **No identifier of a real deployment.** Hostnames, domains, addresses, account ids, keys, people, places and organisations of any real goatnet never enter a file or a commit message. Use the example goatnet `zagros`, documentation addresses (RFC 5737, and `100.127.0.0/16` for mesh), and `example.org` mail. The leak gate (`.github/workflows/leak-gate.yml`) checks every added line against a private list of deployment names. It never prints what matched, so a red leak gate means: rename the identifier. The name list is not available outside CI.
2. **Commits.** Conventional Commits subject of 100 characters or fewer, with a scope (`fix(<component>): …`). Every commit is signed off (`git commit -s`, the DCO) and signed. One logical change per pull request.
3. **Design documents move with the code.** A change to behaviour, data flow, topology or an integration point updates its design document in the same pull request, using the status words built, measured, designed and not built exactly. Decisions are ADRs in [goatcore](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md).

## Before you push

The checks are goatcore scripts reading this environment's files. Check out goatcore at the commit in `goatcore.ref`, copy this repository over it, and from that tree run:

```bash
python3 ops/scripts/standup-config-preflight.py zagros_hosts
python3 ops/scripts/goatlite-render.py --site zagros --check
```
