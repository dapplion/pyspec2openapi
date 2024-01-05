# pyspec2openapi

Tool to convert the types defined in the Ethereum python specs https://github.com/ethereum/consensus-specs to an OpenAPI definition, for https://github.com/ethereum/beacon-APIs. This tool facilitates manteinance of the OpenAPI spec and follows the canonical JSON mapping from https://github.com/ethereum/consensus-specs/pull/3506

## Usage

Install from PyPI

```
pip install pyspec2openapi
```

Create a `config.yml` file

```yaml
version: v1.4.0-beta.5
sources:
  phase0: [beacon-chain.md, validator.md]
  altair: [beacon-chain.md, validator.md]
  bellatrix: [beacon-chain.md, validator.md]
  capella: [beacon-chain.md, validator.md]
  deneb: [polynomial-commitments.md, beacon-chain.md, validator.md]
```

- `version`: Specific Github tag from the `ethereum/consensus-specs` repo to fetch sources from
- `sources`: Topologically sorted list of fork and files to fetch types from. This tool can topologically sort types within the same markdown file, but not across them.

Generate types spec

```
pyspec2openapi config.yml out.yml
```

Review an example output with an [example config](./pyspec2openapi/tests/example_config.yml) in [./pyspec2openapi/tests/example_specs_out.yml](./pyspec2openapi/tests/example_specs_out.yml)
