# Beacon APIs extra types

## Custom types

| Name | SSZ equivalent | Description |
| - | - | - |
| `BlobSidecars` | `List[BlobSidecar, 6]` | |
| `Blobs` | `List[Blob, 4096]` | |
| `KZGProofs` | `List[KZGProof, 4096]` | |

## Containers

The required object for block production according to the Deneb CL spec

```python
class BlockContents(Container):
    block: BeaconBlock
    kzg_proofs: KZGProofs
    blobs: Blobs
```

```python
class SignedBlockContents(Container):
    signed_block: SignedBeaconBlock
    kzg_proofs: KZGProofs
    blobs: Blobs
```

