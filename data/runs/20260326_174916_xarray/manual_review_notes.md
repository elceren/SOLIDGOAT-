# Reviewed Detection Examples

- `SRP` / `AbstractDataStore.get_child_store` / `L331-L333`: reviewed as incorrect. The method is only an abstract contract stub.
- `SRP` / `AbstractWritableDataStore.encode` / `L437-L470`: reviewed as incorrect. The method is longer than ideal, but it still performs a single encode workflow.
- `SRP` / `BackendEntrypoint.open_dataset` / `L777-L792`: reviewed as incorrect. This is an interface-level abstract method, not a concrete SRP violation.

These three reviewed examples suggest the current SRP heuristic is too permissive on abstract APIs and contract methods.
