# Trial Report for xarray

Repository: `/Users/elsteel/xarray`

## Scan Summary
- SRP: 227 detections (227 new, 0 duplicates)
- OCP: 151 detections (151 new, 0 duplicates)
- LSP: 100 detections (100 new, 0 duplicates)
- ISP: 9 detections (9 new, 0 duplicates)
- DIP: 171 detections (171 new, 0 duplicates)

## Baseline Tests
- Success: True

## Manual Review Queue
- SRP in `/Users/elsteel/xarray/xarray/backends/common.py` at `AbstractDataStore.get_child_store` (L331-L333) -> pending_manual_review
- SRP in `/Users/elsteel/xarray/xarray/backends/common.py` at `AbstractWritableDataStore.encode` (L437-L470) -> pending_manual_review
- SRP in `/Users/elsteel/xarray/xarray/backends/common.py` at `BackendEntrypoint.open_dataset` (L777-L792) -> pending_manual_review

## Refactor Attempts
- SRP / AbstractDataStore.get_child_store -> refactor succeeded, tests passed
- SRP / AbstractWritableDataStore.encode -> refactor succeeded, tests passed
