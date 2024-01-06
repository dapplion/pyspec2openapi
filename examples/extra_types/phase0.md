# Beacon APIs extra types

## Containers

### Selection

```python
class BeaconCommitteeSelection(Container):
    validator_index: ValidatorIndex
    slot: Slot
    selection_proof: BLSSignature
```

### API specific types

```python
class DepositSnapshotResponse(Container):
    finalized: Vector[Root, 3]
    deposit_root: Root
    deposit_count: uint64
    execution_block_hash: Root
    execution_block_height: uint64
```

```python
class Committee(Container):
    index: CommitteeIndex
    slot: Slot
    validators: List[ValidatorIndex, 2048]  # List of validator indices assigned to this committee
```

### Duties

```python
class AttesterDuty(Container):
    pubkey: BLSPubkey
    validator_index: ValidatorIndex
    committee_index: CommitteeIndex
    committee_length: uint64
    committees_at_slot: uint64
    validator_committee_index: uint64  # Index of validator in committee
    slot: Slot  # The slot at which the validator must attest
```

```python
class ProposerDuty(Container):
    pubkey: BLSPubkey
    validator_index: ValidatorIndex
    slot: Slot  # The slot at which the validator must propose block
```

```python
class AggregateAndProof(Container):
    aggregator_index: ValidatorIndex
    aggregate: Attestation
    selection_proof: Bytes96
```

```python
class Aggregate(Container):
    aggregator_index: ValidatorIndex
    aggregate: Attestation
```

