# TODO

## Notebook integration tests

Currently the notebook test only checks that all cells execute without errors (`nbconvert --execute`). Future improvements:

- **Strip non-deterministic cells**: Remove or skip cells whose output depends on current time (e.g. `Time()` with no args) and compare remaining outputs against a committed golden standard.
- **Pin all inputs**: Rewrite the notebook so every cell uses fixed values, enabling full output comparison against a golden standard.
