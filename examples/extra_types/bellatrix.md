# Beacon APIs extra types

## Containers

### Registration

From the Builder API specification

```python
class ValidatorRegistration(Container):
    fee_recipient: ExecutionAddress  # Address to receive fees from the block
    gas_limit: uint64  # Preferred gas limit of validator
    timestamp: uint64  # Unix timestamp of registration
    pubkey: BLSPubkey  # BLS public key of validator
```

```python
class SignedValidatorRegistration(Container):
    message: ValidatorRegistration
    signature: BLSSignature
```

