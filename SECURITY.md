# Security and safe validation

Use a supported Python 3.12 interpreter with its latest security patch and a current,
trusted controller image. These repositories do not establish the patch state of
routers, controller hosts, private execution-environment images, or deployed systems.

Run only offline validation in CI. Never use production inventory, credentials,
playbooks, or device connections as a CI test. Resolve and review dependency updates
before use; install the pinned controller requirements where provided. Do not disable
SSH host-key or TLS certificate verification to make a connection work. Provision
verified known-host entries and trusted CA certificates separately, out of band.

The October 2026 certificate incident requires pip >=26.2.2, uv >=0.13.4, and
certifi >=2026.10.19 wherever those tools/packages are used. Updating certifi alone
does not update pip's vendored certificate bundle. Existing installed environments
and private container images must be rebuilt and checked independently.

Security checks here are offline regression checks, not a claim that all installed
or transitive dependencies and remote platforms are free of vulnerabilities.
