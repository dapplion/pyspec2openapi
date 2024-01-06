# Beacon APIs extra types

## Containers

### Selection

```python
class SyncCommitteeSelection(Container):
    validator_index: ValidatorIndex
    slot: Slot  # The slot at which validator is assigned to produce a sync committee contribution
    subcommittee_index: uint64  # SubcommitteeIndex to which the validator is assigned
    selection_proof: BLSSignature  # The `slot_signature` calculated by the validator for the upcoming sync committee slot
```

### Duties

```python
class SyncDuty(Container):
    pubkey: Bytes48
    validator_index: ValidatorIndex
    validator_sync_committee_indices: List[uint64, 512]
```

### Sync committee

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

