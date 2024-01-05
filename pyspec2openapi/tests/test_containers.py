# test_parser.py
import pytest
import json
from ..index import extract_container_code_blocks, extract_custom_types_table, parse_doc, parse_specs

def test_parse_specs():
    sources = {
      'phase0': ['beacon-chain.md', 'validator.md'],
      'altair': ['beacon-chain.md', 'validator.md'],
      'bellatrix': ['beacon-chain.md', 'validator.md'],
      'capella': ['beacon-chain.md', 'validator.md'],
      'deneb': ['polynomial-commitments.md', 'beacon-chain.md', 'validator.md'],
    }
    out = parse_specs('v1.4.0-beta.5', sources)
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

    out = {}
    parse_doc(input, out)
    assert out == {
  "Slot": {
    "$ref": "#/primitive/uint64"
  },
  "Epoch": {
    "$ref": "#/primitive/uint64"
  },
  "CommitteeIndex": {
    "$ref": "#/primitive/uint64"
  },
  "Root": {
    "$ref": "#/primitive/Bytes32"
  },
  "BLSSignature": {
    "$ref": "#/primitive/Bytes96"
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
        "$ref": "#/phase0/AttestationData"
      },
      "signature": {
        "$ref": "#/phase0/BLSSignature"
      }
    }
  }
}


