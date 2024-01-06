# pyspec2openapi

Tool to convert the types defined in the Ethereum python specs https://github.com/ethereum/consensus-specs to an OpenAPI definition, for https://github.com/ethereum/beacon-APIs. This tool facilitates manteinance of the OpenAPI spec and follows the canonical JSON mapping from https://github.com/ethereum/consensus-specs/pull/3506

## Usage

Install from PyPI

```
pip install pyspec2openapi
```

Create a `config.yml` file

```yaml
spec_version: v1.4.0-beta.5
sources:
  phase0:
    - {spec: beacon-chain.md}
    - {spec: validator.md}
    - {file: extra_types/phase0.md}
  altair:
    - {spec: beacon-chain.md}
    - {spec: validator.md}
    - {spec: light-client/sync-protocol.md}
    - {file: extra_types/altair.md}
  bellatrix:
    - {spec: beacon-chain.md}
    - {spec: validator.md}
    - {file: extra_types/bellatrix.md}
  capella:
    - {spec: beacon-chain.md}
    - {spec: validator.md}
    - {spec: light-client/sync-protocol.md}
  deneb:
    - {spec: polynomial-commitments.md}
    - {spec: beacon-chain.md}
    - {spec: validator.md}
    - {spec: p2p-interface.md}
    - {spec: light-client/sync-protocol.md}
    - {file: extra_types/deneb.md}
generate_blinded_types: [bellatrix, capella, deneb]
ignore_classnames:
  - LightClientStore
exclude_comments:
  - '\[New [^\]]*\]'
  - '\[Modified [^\]]*\]'
```

- `spec_version`: Specific Github tag from the `ethereum/consensus-specs` repo to fetch sources from
- `sources`: Topologically sorted list of fork and files to fetch types from. This tool can topologically sort types within the same markdown file, but not across them.
- `generate_blinded_types`: Auto-generate the types `BlindedBeaconBlockBody`, `BlindedBeaconBlock`, and `SignedBlindedBeaconBlock` for a specific set of forks.
- `ignore_classnames`: Ignore container code blocks with this list of names
- `exclude_comments`: Ignore comments for container properties that match any of this regex

Generate types spec

```
pyspec2openapi config.yml out.yml
```

Review an example output with an [example config](./pyspec2openapi/tests/example_config.yml) in [./pyspec2openapi/tests/example_specs_out.yml](./pyspec2openapi/tests/example_specs_out.yml)
