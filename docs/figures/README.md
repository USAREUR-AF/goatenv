# Figures

`make-figures.py` draws every figure in this directory from the tree; nothing in a figure is typed by hand. Each figure is written in a light and a dark variant for a `<picture>` element.

```sh
python3 -I docs/figures/make-figures.py           # write the SVG files
python3 -I docs/figures/make-figures.py --check   # exit 1 if a committed file is out of date
```

| Figure | Shows | Data |
|---|---|---|
| `goatnet-assembly` | goatcore at a pinned release plus this overlay, copied into one checkout and stood up as the LAN goatnet `zagros` | `goatcore.ref`; the four facts in `goatlite.yaml`; the host under `[zagros_hosts]` in `ops/ansible/inventory/mgmt-hosts.ini`; `site_dns_zone`, `has_acme` and the service host names in `ops/ansible/group_vars/zagros_hosts/vars.yml` |

Regenerate after any of those files changes. The generator refuses to draw text wider than its box.

## Checks

Each figure was rendered in headless Chromium as an `<img>` at 830 px and 400 px wide in both themes and inspected. Text is at least 13 units on an 880-unit canvas.
