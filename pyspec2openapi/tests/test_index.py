import json
import yaml
from ..index import (
    extract_container_code_blocks,
    extract_custom_types_table,
    parse_doc,
    parse_specs,
)


def test_parse_specs():
    with open('./examples/config.yml', 'r') as file:
        config = yaml.safe_load(file)

    out = parse_specs(config, './examples')
    print(json.dumps(out, indent=2))


def test_extract_custom_types_table():
    input = """
## Section prev

## Custom types

Some text

| Name | SSZ equivalent | Description |
| - | - | - |
| `Slot` | `uint64` | a slot number |
| `Epoch` | `uint64` | an epoch number |

## Next section
"""
    assert extract_custom_types_table(input) == [
        "| `Slot` | `uint64` | a slot number |",
        "| `Epoch` | `uint64` | an epoch number |"
    ]


def test_extract_container_code_blocks():
    input = """
## Section prev

```python
Not relevant
```

## Containers

### Subsection 1

```python
Relevant code 1
```

### Subsection 2

```python
Relevant code 2
Second line
```

## Next section

```python
Not relevant
```
"""
    assert extract_container_code_blocks(input) == [
        "Relevant code 1",
        """Relevant code 2
Second line"""
            ]


def test_parse_doc():
    input = """
## Custom types

| `Slot` | `uint64` | a slot number |
| `Epoch` | `uint64` | an epoch number |
| `CommitteeIndex` | `uint64` | a committee index at a slot |
| `Root` | `Bytes32` | a Merkle root |
| `BLSSignature` | `Bytes96` | a BLS12-381 signature |

## Containers

```python
class Checkpoint(Container):
    epoch: Epoch
    root: Root
```

```python
class AttestationData(Container):
    slot: Slot
    index: CommitteeIndex
    # LMD GHOST vote
    beacon_block_root: Root
    # FFG vote
    source: Checkpoint
    target: Checkpoint
```

```python
class Attestation(Container):
    aggregation_bits: Bitlist[MAX_VALIDATORS_PER_COMMITTEE]
    data: AttestationData  # Some comment in the same line
    # Some comment before the property
    signature: BLSSignature
```

## Next section
"""

    config = {
        'dependants': {},
        'mutations': {'phase0': []},
        'class_code': {}
    }
    out = {
        'primitive': {
            'boolean': {'type': 'boolean', 'example': False},
            'uint64': {'type': 'string', 'example': '1'},
        },
        'phase0': {}
    }
    parse_doc(input, 'phase0', config, out)
    assert out == {
        'primitive': {
            'boolean': {'type': 'boolean', 'example': False},
            'uint64': {'type': 'string', 'example': '1'},
            'Bytes32': {
                'type': 'string',
                'format': 'hex',
                'example': "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                'pattern': "^0x[a-fA-F0-9]{64}$",
            },
            'Bytes96': {
                'type': 'string',
                'format': 'hex',
                'example': "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",  # noqa: E501
                'pattern': "^0x[a-fA-F0-9]{192}$",
            }
        },
        "phase0": {
            "Slot": {
              "allOf": [
                {"$ref": "#/primitive/uint64"},
                {"description": "a slot number"}
              ]
            },
            "Epoch": {
              "allOf": [
                {"$ref": "#/primitive/uint64"},
                {"description": "an epoch number"}
              ]
            },
            "CommitteeIndex": {
              "allOf": [
                {"$ref": "#/primitive/uint64"},
                {"description": "a committee index at a slot"}
              ]
            },
            "Root": {
              "allOf": [
                {"$ref": "#/primitive/Bytes32"},
                {"description": "a Merkle root"}
              ]
            },
            "BLSSignature": {
              "allOf": [
                {"$ref": "#/primitive/Bytes96"},
                {"description": "a BLS12-381 signature"}
              ]
            },
            "Checkpoint": {
                "type": "object",
                "properties": {
                  "epoch": {
                    "$ref": "#/phase0/Epoch"
                  },
                  "root": {
                    "$ref": "#/phase0/Root"
                  }
                }
              },
            "AttestationData": {
                "type": "object",
                "properties": {
                  "slot": {
                    "$ref": "#/phase0/Slot"
                  },
                  "index": {
                    "$ref": "#/phase0/CommitteeIndex"
                  },
                  "beacon_block_root": {
                    "$ref": "#/phase0/Root"
                  },
                  "source": {
                    "$ref": "#/phase0/Checkpoint"
                  },
                  "target": {
                    "$ref": "#/phase0/Checkpoint"
                  }
                }
              },
            "Attestation": {
                "type": "object",
                "properties": {
                  "aggregation_bits": {
                    "$ref": "#/primitive/Bitlist"
                  },
                  "data": {
                      "allOf": [
                          {"$ref": "#/phase0/AttestationData"},
                          {"description": "Some comment in the same line"}
                      ]
                  },
                  "signature": {
                    "$ref": "#/phase0/BLSSignature"
                  }
                }
              }
            }
        }
