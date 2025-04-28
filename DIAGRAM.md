### Make sure to view this in the browser to see the built flowchart!
```mermaid
flowchart TD
    A[Party requests insurance through Broker] --> B[Broker submits application to reThought]
    B --> C[Underwriter and system assess risk]
    C --> D{Eligible for coverage?}
    D -- Yes --> E[reThought issues Quote]
    E --> F[Broker sends Quote to Party]
    F --> G{Party accepts Quote?}
    G -- Yes --> H[Broker sends Binder to reThought]
    H --> I[reThought sends Policy to Broker and Insured]
    I --> J[Insured pays Broker → Broker pays reThought]
    J --> K{If Loss Occurs}
    K --> L[Insured submits Claim → Adjuster determines payout]

    D -- No --> M[Coverage Denied]
    G -- No --> N[No Policy Issued]
