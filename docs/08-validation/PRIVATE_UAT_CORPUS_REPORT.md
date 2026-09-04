# Private UAT Corpus API and Batch Report

Generated: 2026-09-04T05:56:52.606292+00:00

## Outcome

- Selected files: 223
- Accepted images: 221
- Skipped non-images: 2
- Individual API processing passes: 221
- Individual API processing failures: 0
- Grouped product API processing passes: 152
- Grouped product API processing failures: 0
- Suggested product groups: 152
- Maximum images in a group: 3
- Functional gate: PASS
- Performance gate: PASS
- Complete gate: PASS
- Equivalent cross-format panel integration: PASS

## Performance

| Scope | Average | Median | P95 | Maximum | Average target | Hard-case target |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Individual images | 3.997 s | 3.895 s | 6.748 s | 7.874 s | PASS | PASS |
| Grouped products | 1.014 s | 0.629 s | 2.693 s | 6.607 s | PASS | PASS |

## Equivalent cross-format panel integration

A content-only scan selected two visually equivalent files with different encodings. The first analysis request after fresh application readiness returned HTTP 200 in 6.226 seconds, retained 2 panel records, and recorded 1 duplicate link. Worker generation was 1 before and 1 after the request.

## Accuracy boundary

This run proves admission, decode, OCR completion, 24-check contract integrity, original-pixel evidence integrity, grouping, product reruns, and latency through the production multipart API. It does not turn label-derived text into an independent application record.

The local oracle contains 50 cases. Exactly 42 current filenames match it, 179 current images are not covered, and 8 oracle filenames are absent. A complete current-corpus human oracle is therefore required before claiming field-level or legal-label accuracy for the current corpus.

## Per-image production API results

| Case | Artifact | API | Time | Type | Brand read | Class read | ABV | Proof | Net contents | Producer read | Origin read | Machine finding |
| --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| image-001 | 6a788b8324ad | 200 | 4.611 s | wine | Yes | Yes | 13.5 | Not read | 750 mL | No | Yes | Review needed |
| image-002 | 5571877cae7a | 200 | 3.868 s | wine | Yes | Yes | 13.5 | Not read | 750 mL | No | Yes | Review needed |
| image-003 | 06f4c17786bc | 200 | 5.351 s | Not read | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-004 | 6e34340aab68 | 200 | 7.573 s | distilled_spirits | Yes | Yes | 40.0 | Not read | 750 mL | No | No | Review needed |
| image-005 | bd3e70e5f201 | 200 | 3.398 s | Not read | Yes | No | Not read | Not read | 750 mL | No | No | Review needed |
| image-006 | 33f015db1f73 | 200 | 2.663 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-007 | 063c97e2a453 | 200 | 4.862 s | Not read | Yes | No | 45.0 | Not read | 750 mL | No | No | Review needed |
| image-008 | 90b052980d75 | 200 | 4.176 s | Not read | Yes | No | Not read | Not read | 750 mL | No | No | Review needed |
| image-009 | cd66bbf0e9c1 | 200 | 3.288 s | distilled_spirits | Yes | Yes | 45.0 | Not read | Not read | No | No | Review needed |
| image-010 | 49349103c39f | 200 | 4.337 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-011 | ee288047c742 | 200 | 3.037 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-012 | 950a1b762100 | 200 | 3.205 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-013 | e2e1b98e156c | 200 | 4.134 s | wine | Yes | Yes | 13.2 | Not read | 750 mL | No | No | Review needed |
| image-014 | c80c33db058f | 200 | 4.680 s | malt_beverage | Yes | Yes | 7.2 | Not read | 16 fl oz | Yes | No | Review needed |
| image-015 | 260fd6c45b30 | 200 | 4.796 s | wine | Yes | Yes | 11.5 | Not read | 750 mL | Yes | No | Review needed |
| image-016 | b1bb7e557e6c | 200 | 2.454 s | wine | Yes | Yes | 12.0 | Not read | 750 mL | Yes | No | Review needed |
| image-017 | 0cfb1e62d8f7 | 200 | 4.839 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | No | Review needed |
| image-018 | 579f311533f1 | 200 | 4.495 s | wine | Yes | No | 13.2 | Not read | 750 mL | Yes | No | Review needed |
| image-019 | 1633f7908cf0 | 200 | 4.517 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 1.75 L | Yes | No | Review needed |
| image-020 | d6d77f304aa3 | 200 | 5.034 s | wine | Yes | Yes | 0.0 | Not read | 150 mL | Yes | Yes | Review needed |
| image-021 | 68200c99e6e6 | 200 | 6.659 s | Not read | Yes | No | 5.0 | Not read | 150 mL | No | No | Review needed |
| image-022 | f690a1f3cdc4 | 200 | 1.838 s | wine | Yes | Yes | 0.0 | Not read | 750 mL | No | No | Review needed |
| image-023 | 04b5e9ea6175 | 200 | 4.371 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-024 | c9d51cbcb1eb | 200 | 2.813 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | Yes | Review needed |
| image-025 | 2c6c1af13d41 | 200 | 4.896 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-026 | 01b1916cb775 | 200 | 4.507 s | distilled_spirits | Yes | Yes | 40.0 | Not read | Not read | Yes | No | Review needed |
| image-027 | c1ea6555cade | 200 | 5.077 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | Yes | Yes | Review needed |
| image-028 | e87fff90ae9c | 200 | 3.202 s | distilled_spirits | Yes | No | 53.5 | 107.0 | 750 mL | No | No | Review needed |
| image-029 | c1f4eb91616f | 200 | 4.179 s | distilled_spirits | Yes | Yes | 53.5 | 107.0 | 750 mL | Yes | No | Review needed |
| image-030 | 7c5d65bf352d | 200 | 4.784 s | distilled_spirits | Yes | Yes | 53.5 | Not read | 750 mL | Yes | No | Review needed |
| image-031 | 813c708d4ce5 | 200 | 4.460 s | distilled_spirits | Yes | Yes | Not read | Not read | 5 mL | Yes | No | Review needed |
| image-032 | e03ea09c3229 | 200 | 2.197 s | distilled_spirits | Yes | Yes | 47.0 | Not read | 750 mL | No | No | Review needed |
| image-033 | ce8421e91296 | 200 | 5.723 s | Not read | Yes | No | Not read | Not read | 750 mL | No | No | Review needed |
| image-034 | 0c8aad2aa219 | 200 | 4.043 s | distilled_spirits | Yes | No | 50.0 | 100.0 | Not read | No | No | Review needed |
| image-035 | c82654f4878a | 200 | 7.494 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-036 | 8468d87da757 | 200 | 4.004 s | distilled_spirits | Yes | Yes | 30.0 | Not read | 750 mL | No | No | Review needed |
| image-037 | 4eaf0c980dd6 | 200 | 2.727 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-038 | 1ff2f9a534f2 | 200 | 4.414 s | Not read | No | No | 35.0 | Not read | 750 mL | No | No | Review needed |
| image-039 | d5cf1c704d71 | 200 | 3.173 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-040 | ccf254edd102 | 200 | 3.290 s | distilled_spirits | Yes | Yes | 58.35 | Not read | Not read | No | No | Review needed |
| image-041 | 0140a9ae1c7f | 200 | 3.887 s | wine | Yes | Yes | 12.8 | Not read | 750 mL | Yes | No | Review needed |
| image-042 | 562b50aa4063 | 200 | 3.700 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | No | No | Review needed |
| image-043 | cd9fba9c2c80 | 200 | 4.611 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-044 | 604a94080ce4 | 200 | 5.710 s | wine | Yes | Yes | 12.5 | Not read | 750 mL | No | No | Review needed |
| image-045 | 0c87ed0b6921 | 200 | 3.434 s | distilled_spirits | Yes | Yes | 48.2 | Not read | 700 mL | Yes | No | Review needed |
| image-046 | 3267b9d184a0 | 200 | 6.105 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-047 | 45418bee02f8 | 200 | 6.310 s | distilled_spirits | Yes | Yes | 40.0 | Not read | 1.5 fl oz | Yes | No | Review needed |
| image-048 | dbb1a030565a | 200 | 3.172 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | No | Review needed |
| image-049 | 8d1a125dae29 | 200 | 4.695 s | Not read | Yes | No | 40.0 | Not read | 750 mL | No | Yes | Review needed |
| image-050 | 4e8a2b1cb1a9 | 200 | 7.191 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-051 | 7f730260eb2a | 200 | 5.212 s | wine | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-052 | 8e353dc63c8f | 200 | 2.687 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-053 | 19c787ef85d0 | 200 | 5.079 s | Not read | Yes | No | 12.0 | Not read | Not read | No | No | Review needed |
| image-054 | 5cd0225c97e8 | 200 | 2.956 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-055 | 7dc7ba18bf4a | 200 | 5.418 s | wine | Yes | No | 14.0 | Not read | 750 mL | No | Yes | Review needed |
| image-056 | 7735e222d4a6 | 200 | 3.395 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-057 | 53f7dc3148f1 | 200 | 4.057 s | distilled_spirits | Yes | Yes | 40.0 | Not read | 375 mL | No | Yes | Review needed |
| image-058 | b5dab368c65f | 200 | 4.763 s | Not read | Yes | No | Not read | Not read | Not read | Yes | Yes | Review needed |
| image-059 | 3c7fd33ea268 | 200 | 6.050 s | distilled_spirits | Yes | Yes | 35.0 | 70.0 | 750 mL | No | No | Review needed |
| image-060 | 66c3d4443c94 | 200 | 4.906 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | Yes | No | Review needed |
| image-061 | e6391a4fa13c | 200 | 7.043 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | Yes | Yes | Review needed |
| image-062 | 841026008ec3 | 200 | 4.173 s | distilled_spirits | Yes | Yes | 40.0 | Not read | Not read | No | No | Review needed |
| image-063 | 4a196467aa7a | 200 | 4.224 s | wine | Yes | Yes | 12.5 | Not read | 750 mL | Yes | Yes | Review needed |
| image-064 | 80da552ab338 | 200 | 4.923 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-065 | b6d01f8588cf | 200 | 5.569 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 1.5 fl oz | No | No | Review needed |
| image-066 | 3a0c8bbd02c3 | 200 | 4.671 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | No | No | Review needed |
| image-067 | 2d6b8424b0ab | 200 | 3.540 s | distilled_spirits | Yes | Yes | 58.5 | 117.0 | 750 mL | No | No | Review needed |
| image-068 | f914010d2f5b | 200 | 3.806 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-069 | ec7d8df7eead | 200 | 4.048 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-070 | 022e5bc4f2ac | 200 | 4.077 s | wine | Yes | Yes | 12.0 | Not read | 750 mL | Yes | Yes | Review needed |
| image-071 | 38be9cd9e528 | 200 | 3.972 s | Not read | Yes | No | 13.0 | Not read | 750 mL | No | No | Review needed |
| image-072 | 25138650050b | 200 | 4.987 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-073 | 4523eac5509c | 200 | 3.092 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-074 | 7f0a605167ea | 200 | 4.088 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-075 | 9bf61c451042 | 200 | 2.369 s | Not read | Yes | No | Not read | Not read | 750 mL | No | No | Review needed |
| image-076 | c583e45ba40e | 200 | 4.166 s | distilled_spirits | Yes | No | Not read | Not read | 5750 mL | Yes | No | Review needed |
| image-077 | 733382500797 | 200 | 4.370 s | distilled_spirits | Yes | Yes | 47.0 | Not read | Not read | No | No | Review needed |
| image-078 | 1f18394599da | 200 | 4.617 s | distilled_spirits | Yes | No | 45.0 | 90.0 | 750 mL | Yes | Yes | Review needed |
| image-079 | 54a8bf178089 | 200 | 6.715 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | Yes | No | Review needed |
| image-080 | 090e148bb954 | 200 | 3.117 s | distilled_spirits | Yes | No | Not read | 66.0 | Not read | No | No | Review needed |
| image-081 | bac11b9c6cf5 | 200 | 4.910 s | distilled_spirits | Yes | Yes | 40.0 | Not read | Not read | No | No | Review needed |
| image-082 | 26342ef1960d | 200 | 4.903 s | Not read | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-083 | 05602e611e18 | 200 | 3.055 s | Not read | Yes | No | 11.0 | Not read | Not read | No | No | Review needed |
| image-084 | 95628dbee3c1 | 200 | 3.491 s | Not read | Yes | No | 11.0 | Not read | Not read | Yes | No | Review needed |
| image-085 | 3db0227b4214 | 200 | 2.424 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-086 | b90d3b6c8e92 | 200 | 2.515 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-087 | f8b4a622d453 | 200 | 7.294 s | distilled_spirits | Yes | Yes | 43.0 | Not read | 750 mL | No | No | Review needed |
| image-088 | e1eb0ae4e9dc | 200 | 3.999 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | Yes | Review needed |
| image-089 | 6821a9aa38ea | 200 | 4.440 s | distilled_spirits | Yes | Yes | 45.0 | 90.0 | 750 mL | Yes | No | Review needed |
| image-090 | 6de64a56e6d7 | 200 | 2.905 s | malt_beverage | Yes | Yes | 7.2 | Not read | 16 fl oz | Yes | No | Review needed |
| image-091 | 1c8ae59cbab6 | 200 | 4.162 s | distilled_spirits | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-092 | e181455ea573 | 200 | 3.731 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 375 mL | Yes | No | Review needed |
| image-093 | f022713fb8fa | 200 | 7.874 s | distilled_spirits | Yes | Yes | Not read | Not read | 1 L | Yes | No | Review needed |
| image-094 | b09bf6c06da9 | 200 | 7.666 s | distilled_spirits | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-095 | 97e3fc92a74f | 200 | 6.815 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-096 | cf4261089265 | 200 | 6.333 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-097 | 1f25521bf5bf | 200 | 5.351 s | distilled_spirits | Yes | Yes | 35.0 | 70.0 | 1 L | No | No | Review needed |
| image-098 | 1eb38bebe394 | 200 | 6.722 s | distilled_spirits | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-099 | 243222f8614d | 200 | 2.818 s | malt_beverage | Yes | Yes | 9.5 | Not read | 12 fl oz | Yes | No | Review needed |
| image-100 | faa2429b6479 | 200 | 3.824 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | Not read | No | No | Review needed |
| image-101 | e68dabad285f | 200 | 6.748 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 1.75 L | No | No | Review needed |
| image-102 | bdf25746be63 | 200 | 4.423 s | Not read | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-103 | e2f74373b756 | 200 | 4.080 s | distilled_spirits | Yes | No | 40.0 | 80.0 | 750 mL | No | No | Review needed |
| image-104 | 5d3da8efcce8 | 200 | 4.585 s | wine | Yes | Yes | 13.8 | Not read | 750 mL | Yes | No | Review needed |
| image-105 | 05382e77adef | 200 | 3.484 s | distilled_spirits | Yes | Yes | 47.0 | 94.0 | 1 L | No | No | Review needed |
| image-106 | 196d6c303e3e | 200 | 5.307 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | Yes | No | Review needed |
| image-107 | 32e8e12dba8d | 200 | 4.210 s | distilled_spirits | Yes | Yes | 45.0 | Not read | 750 mL | No | No | Review needed |
| image-108 | f0249a129f1a | 200 | 6.186 s | distilled_spirits | Yes | Yes | 40.0 | Not read | 700 mL | Yes | Yes | Review needed |
| image-109 | 671529f08541 | 200 | 5.140 s | Not read | Yes | Yes | 40.0 | Not read | Not read | No | No | Review needed |
| image-110 | 38a7962053e8 | 200 | 4.222 s | wine | Yes | Yes | 12.5 | Not read | Not read | Yes | Yes | Review needed |
| image-111 | e894f97a1c3b | 200 | 3.930 s | wine | Yes | Yes | 12.5 | Not read | Not read | Yes | Yes | Review needed |
| image-112 | 39ea88c7bbf0 | 200 | 2.639 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-113 | ca96a8cad116 | 200 | 4.886 s | Not read | Yes | Yes | 40.0 | Not read | Not read | Yes | Yes | Review needed |
| image-114 | a78c24cdb1a3 | 200 | 3.428 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-115 | 354a7f25c37c | 200 | 2.299 s | distilled_spirits | Yes | Yes | 35.0 | 70.0 | 750 mL | No | No | Review needed |
| image-116 | c6ca14c1ad5d | 200 | 3.533 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-117 | 7d26605d34f8 | 200 | 2.050 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-118 | 9d0696e152bd | 200 | 2.492 s | malt_beverage | Yes | Yes | 5.0 | Not read | 16 fl oz | Yes | No | Review needed |
| image-119 | 1da66972d68e | 200 | 3.192 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-120 | 00951453f0e5 | 200 | 6.867 s | distilled_spirits | Yes | Yes | 47.5 | Not read | 700 mL | No | No | Review needed |
| image-121 | ef3cc45a6d84 | 200 | 3.693 s | distilled_spirits | Yes | No | 47.5 | 95.0 | 700 mL | No | No | Review needed |
| image-122 | 41d6135b09f0 | 200 | 2.220 s | Not read | Yes | No | 8.5 | Not read | Not read | No | No | Review needed |
| image-123 | 8c78bee0a0f6 | 200 | 4.753 s | wine | Yes | Yes | 13.5 | Not read | 750 mL | Yes | No | Review needed |
| image-124 | 1f05614804a7 | 200 | 3.582 s | distilled_spirits | Yes | Yes | 44.5 | 89.0 | 750 mL | No | No | Review needed |
| image-125 | 43a2ca452ccf | 200 | 5.094 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-126 | 790167fec0d1 | 200 | 3.801 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-127 | b964d7f5431c | 200 | 3.054 s | distilled_spirits | Yes | Yes | Not read | 85.0 | Not read | No | No | Review needed |
| image-128 | 18191b418bed | 200 | 3.227 s | distilled_spirits | Yes | Yes | Not read | 85.0 | Not read | No | No | Review needed |
| image-129 | d1ce3dfacd7c | 200 | 6.327 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | Yes | No | Review needed |
| image-130 | c98d91a71955 | 200 | 4.098 s | distilled_spirits | Yes | Yes | 30.0 | 60.0 | 750 mL | Yes | No | Review needed |
| image-131 | 056940e2892c | 200 | 3.480 s | Not read | Yes | No | Not read | Not read | 750 mL | Yes | No | Review needed |
| image-132 | 148e612e5732 | 200 | 2.912 s | distilled_spirits | No | No | 40.0 | 80.0 | Not read | No | No | Review needed |
| image-133 | 6ce55fea8a30 | 200 | 2.824 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-134 | 0735da62bd73 | 200 | 5.369 s | distilled_spirits | Yes | Yes | 40.0 | Not read | 750 mL | No | Yes | Review needed |
| image-135 | b28fad30a767 | 200 | 3.445 s | distilled_spirits | Yes | Yes | 40.0 | Not read | 750 mL | No | No | Review needed |
| image-136 | bfb0f1ce0d4d | 200 | 4.038 s | distilled_spirits | Yes | Yes | 40.0 | Not read | 750 mL | No | Yes | Review needed |
| image-137 | a8eff2f31131 | 200 | 2.846 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | No | No | Review needed |
| image-138 | 2cfc80945da0 | 200 | 2.247 s | distilled_spirits | Yes | Yes | 47.0 | 94.0 | 1 L | Yes | No | Review needed |
| image-139 | c00bc6488e06 | 200 | 2.130 s | wine | Yes | No | 12.0 | Not read | 750 mL | Yes | No | Review needed |
| image-140 | 39c3ba4c7691 | 200 | 2.246 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-141 | 1c644293b2ae | 200 | 5.285 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-142 | b1ed7327ad68 | 200 | 3.530 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | No | No | Review needed |
| image-143 | 134d76be05e4 | 200 | 0.344 s | malt_beverage | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-144 | ba6d53e5989b | 200 | 5.254 s | malt_beverage | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-145 | 134d76be05e4 | 200 | 0.341 s | malt_beverage | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-146 | babe75673f58 | 200 | 3.214 s | Not read | Yes | No | 7.0 | Not read | 12 fl oz | No | No | Review needed |
| image-147 | babe75673f58 | 200 | 0.497 s | Not read | Yes | No | 7.0 | Not read | 12 fl oz | No | No | Review needed |
| image-148 | f44d7f2347f4 | 200 | 3.359 s | wine | Yes | No | 14.0 | Not read | Not read | No | Yes | Review needed |
| image-149 | f742e70394ab | 200 | 3.431 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-150 | 962ed59ea35c | 200 | 4.339 s | wine | Yes | Yes | 12.0 | Not read | 750 mL | No | Yes | Review needed |
| image-151 | 938b4f397464 | 200 | 3.092 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-152 | 15e3518d13c3 | 200 | 6.708 s | distilled_spirits | Yes | Yes | 35.0 | 70.0 | Not read | No | No | Review needed |
| image-153 | d7e6eea86a2e | 200 | 4.728 s | Not read | Yes | No | Not read | Not read | 750 mL | No | No | Review needed |
| image-154 | 4ccadbc9c61e | 200 | 5.755 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | Yes | No | Review needed |
| image-155 | 67c9c5bb9fe3 | 200 | 6.537 s | distilled_spirits | Yes | Yes | 35.0 | 70.0 | Not read | No | No | Review needed |
| image-156 | 065cc4129995 | 200 | 4.881 s | distilled_spirits | Yes | Yes | 46.0 | Not read | 1.5 fl oz | Yes | No | Review needed |
| image-157 | d0bbba6aa1f0 | 200 | 3.887 s | distilled_spirits | Yes | Yes | 46.0 | Not read | Not read | No | No | Review needed |
| image-158 | ec61ee3542e6 | 200 | 5.296 s | distilled_spirits | Yes | Yes | 35.0 | Not read | Not read | No | No | Review needed |
| image-159 | 2effd51377c0 | 200 | 7.217 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-160 | 1748e4fac7f1 | 200 | 3.475 s | distilled_spirits | Yes | Yes | Not read | Not read | 750 mL | No | No | Review needed |
| image-161 | 3b6c11b6b0d1 | 200 | 3.584 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-162 | a92bbea70d40 | 200 | 2.488 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-163 | 7dd3d3e0b295 | 200 | 4.101 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-164 | 53f2ebf8ece5 | 200 | 3.177 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-165 | 0b9029abf756 | 200 | 5.607 s | malt_beverage | Yes | Yes | 8.5 | Not read | Not read | Yes | No | Review needed |
| image-166 | 4bfbe708bf3f | 200 | 2.669 s | malt_beverage | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-167 | 434dd1f1acae | 200 | 3.039 s | Not read | Yes | No | Not read | Not read | Not read | Yes | No | Review needed |
| image-168 | d0c94c8db242 | 200 | 3.454 s | wine | Yes | Yes | 14.5 | Not read | 750 mL | Yes | No | Review needed |
| image-169 | 0dba51a621d1 | 200 | 2.981 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | No | Differences detected |
| image-170 | 831e7b6e7475 | 200 | 3.990 s | distilled_spirits | Yes | Yes | 38.0 | 76.0 | 750 mL | Yes | Yes | Differences detected |
| image-171 | db21d752cb16 | 200 | 3.521 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 1.75 L | Yes | No | Review needed |
| image-172 | 05bd44ad4d37 | 200 | 2.961 s | distilled_spirits | Yes | Yes | 47.0 | 94.0 | 1 L | Yes | No | Review needed |
| image-173 | c72950509da8 | 200 | 2.140 s | distilled_spirits | Yes | Yes | 47.0 | 94.0 | 1 L | Yes | No | Review needed |
| image-174 | c106d6b32c53 | 200 | 2.315 s | malt_beverage | Yes | Yes | 9.5 | Not read | 12 fl oz | Yes | No | Review needed |
| image-175 | 9fa8dfbda262 | 200 | 3.239 s | wine | Yes | Yes | 12.0 | Not read | 750 mL | Yes | Yes | Review needed |
| image-176 | 216d04aa76d2 | 200 | 2.652 s | malt_beverage | Yes | Yes | 7.2 | Not read | 16 fl oz | Yes | No | Review needed |
| image-177 | ec3f85d61286 | 200 | 0.216 s | distilled_spirits | Yes | Yes | 47.0 | 94.0 | 1 L | No | No | Review needed |
| image-178 | 1f2aa36de8e7 | 200 | 3.383 s | distilled_spirits | Yes | Yes | 45.0 | 90.0 | 750 mL | Yes | No | Review needed |
| image-179 | d1ded5c5d96c | 200 | 2.493 s | distilled_spirits | Yes | Yes | 45.0 | 90.0 | 750 mL | Yes | No | Review needed |
| image-180 | d1e52a4d7176 | 200 | 3.959 s | wine | Yes | Yes | 12.5 | Not read | 750 mL | Yes | No | Review needed |
| image-181 | 7c0974f885c8 | 200 | 3.200 s | wine | Yes | Yes | 12.0 | Not read | 750 mL | Yes | Yes | Review needed |
| image-182 | 3b0a5c4fa9be | 200 | 3.598 s | distilled_spirits | Yes | Yes | 45.0 | 90.0 | 750 mL | Yes | No | Review needed |
| image-183 | 5938a5d51f19 | 200 | 2.136 s | malt_beverage | Yes | Yes | 7.2 | Not read | 16 fl oz | Yes | No | Review needed |
| image-184 | 1b6ef63c7ba0 | 200 | 3.156 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | Yes | No differences found in checked fields |
| image-185 | 0d7407b4fd23 | 200 | 2.516 s | malt_beverage | Yes | Yes | 9.5 | Not read | 12 fl oz | Yes | No | Review needed |
| image-186 | 4808aefa27d7 | 200 | 4.019 s | wine | Yes | Yes | 12.0 | Not read | 750 mL | Yes | No | Review needed |
| image-187 | 5b838cd6b31b | 200 | 3.537 s | wine | Yes | Yes | 13.5 | Not read | 750 mL | Yes | No | Review needed |
| image-188 | 421610adf8f1 | 200 | 2.895 s | malt_beverage | Yes | Yes | 5.2 | Not read | 12 fl oz | Yes | No | No differences found in checked fields |
| image-189 | 82aab01022e9 | 200 | 2.117 s | distilled_spirits | Yes | Yes | 47.0 | 94.0 | 1 L | Yes | No | Review needed |
| image-190 | 68f9446a6109 | 200 | 3.895 s | wine | Yes | Yes | 13.0 | Not read | 750 mL | Yes | No | Review needed |
| image-191 | c78d4226e0f9 | 200 | 2.771 s | wine | Yes | Yes | 13.8 | Not read | 750 mL | Yes | No | Review needed |
| image-192 | ecd8c73d2bba | 200 | 3.823 s | wine | Yes | Yes | 13.5 | Not read | 750 mL | Yes | No | Review needed |
| image-193 | c21ef19f4d9b | 200 | 4.335 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | Yes | No differences found in checked fields |
| image-194 | 377339e49675 | 200 | 2.815 s | distilled_spirits | Yes | Yes | 47.0 | 94.0 | 1 L | Yes | No | Review needed |
| image-195 | 1870ec708df5 | 200 | 3.542 s | malt_beverage | Yes | Yes | 5.2 | Not read | 12 fl oz | No | No | Review needed |
| image-196 | 8e06132a6fc1 | 200 | 4.916 s | wine | Yes | Yes | 13.5 | Not read | 750 mL | No | No | Review needed |
| image-197 | e095eedff01c | 200 | 2.977 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | Yes | Review needed |
| image-198 | 4d10941df2f3 | 200 | 3.529 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 1.75 L | Yes | No | No differences found in checked fields |
| image-199 | ebf718813ee6 | 200 | 3.934 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 1 L | Yes | No | Differences detected |
| image-200 | 2b999eb5aa02 | 200 | 2.709 s | distilled_spirits | Yes | No | 40.0 | 80.0 | Not read | No | No | Review needed |
| image-201 | fd9f4a718b78 | 200 | 3.956 s | Not read | Yes | No | Not read | Not read | 1.75 L | Yes | No | Review needed |
| image-202 | 43984db2ed8e | 200 | 3.008 s | malt_beverage | Yes | Yes | 5.2 | Not read | 12 fl oz | No | No | Review needed |
| image-203 | 2bf1fa9063db | 200 | 4.040 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | Yes | No | Review needed |
| image-204 | 827e76f50359 | 200 | 2.330 s | distilled_spirits | No | Yes | 40.0 | 80.0 | 750 mL | No | No | Review needed |
| image-205 | c1d6d4e2c90b | 200 | 4.097 s | distilled_spirits | Yes | Yes | 0.0 | Not read | Not read | No | No | Review needed |
| image-206 | d647a45890bf | 200 | 4.451 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-207 | 0a3bf676df83 | 200 | 2.297 s | distilled_spirits | Yes | Yes | 100.0 | Not read | Not read | No | No | Review needed |
| image-208 | 28a0a543ae66 | 200 | 2.542 s | distilled_spirits | Yes | Yes | 40.0 | Not read | Not read | No | No | Review needed |
| image-209 | 1d06d29625aa | 200 | 3.234 s | distilled_spirits | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-210 | bad36dbeb723 | 200 | 2.258 s | distilled_spirits | Yes | Yes | Not read | 80.0 | 750 mL | No | No | Review needed |
| image-211 | e5e16b8a560f | 200 | 7.513 s | distilled_spirits | Yes | No | Not read | Not read | 750 mL | Yes | No | Review needed |
| image-212 | 4c9e8c599829 | 200 | 3.415 s | distilled_spirits | Yes | Yes | 50.5 | 101.0 | 750 mL | No | No | Review needed |
| image-213 | 23d4e5d24532 | 200 | 3.857 s | wine | Yes | Yes | Not read | Not read | Not read | No | No | Review needed |
| image-214 | 83bdced2d8a0 | 200 | 5.080 s | wine | Yes | No | 100.0 | Not read | 750 mL | Yes | No | Review needed |
| image-215 | 76a73c22d359 | 200 | 2.084 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-216 | e920faba150f | 200 | 4.168 s | wine | Yes | Yes | 13.5 | Not read | 750 mL | No | No | Review needed |
| image-217 | 6f52d8398ead | 200 | 2.592 s | distilled_spirits | Yes | Yes | 40.0 | 80.0 | 750 mL | Yes | Yes | Review needed |
| image-218 | a3db68913b57 | 200 | 2.834 s | wine | Yes | Yes | 16.0 | Not read | 750 mL | No | No | Review needed |
| image-219 | 6dd2fde24274 | 200 | 2.251 s | Not read | Yes | No | 16.0 | Not read | Not read | No | No | Review needed |
| image-220 | 715a16e09c28 | 200 | 4.376 s | Not read | Yes | No | Not read | Not read | Not read | No | No | Review needed |
| image-221 | 60aa57490c5d | 200 | 3.047 s | Not read | Yes | No | 53.5 | Not read | 750 mL | No | No | Review needed |
