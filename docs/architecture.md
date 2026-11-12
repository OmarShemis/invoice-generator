# Architecture

```mermaid
flowchart LR
Form --> Validation
Validation --> DecimalAmounts
DecimalAmounts --> PDF
```

See the source modules and tests for implementation details. External model/API availability is independent of offline test success.
