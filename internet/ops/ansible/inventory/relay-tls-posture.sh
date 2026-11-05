# shellcheck shell=bash
# Each goatnet's relay TLS posture, read by generate-relays.sh: le-dns01 (publicly trusted,
# Cloudflare DNS-01) or self-signed. A goatnet with no row is refused. goatlite adds its row here.
relay_tls_posture_for() {
  case "$1" in
    # BEGIN goatlite example-internet
    # goatlite grown to the internet (ADR 1213): peers enrol from anywhere, so the
    # relays need publicly trusted certificates; rendered by ops/scripts/goatlite-render.py.
    example-internet) echo le-dns01 ;;
    # END goatlite example-internet
    *) return 1 ;;
  esac
}
