# Beacon APIs extra types

## Containers

### Selection

```python
class BeaconCommitteeSelection(Container):
    validator_index: ValidatorIndex
    slot: Slot
    selection_proof: BLSSignature
```

```python
class SyncCommitteeSelection(Container):
    validator_index: ValidatorIndex
    slot: Slot  # The slot at which validator is assigned to produce a sync committee contribution
    subcommittee_index: uint64  # SubcommitteeIndex to which the validator is assigned
    selection_proof: BLSSignature  # The `slot_signature` calculated by the validator for the upcoming sync committee slot
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
class SyncDuty(Container):
    pubkey: Bytes48
    validator_index: ValidatorIndex
    validator_sync_committee_indices: List[uint64, 512]
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

### Altair

```python
class SyncCommitteeSignature(Container):
    slot: Slot
    beacon_block_root: Root
    validator_index: ValidatorIndex
    signature: BLSSignature
```

```python
class SyncCommitteeSubscription(Container):
    validator_index: ValidatorIndex
    sync_committee_indices: List[uint64, 64]
    until_epoch: Epoch  # The final epoch (exclusive value) that the specified validator requires the subscription for
```

