# Source Context

## Source inventory

| Source ID | Source | Class | Retrieved / supplied | Normative use |
|---|---|---|---|---|
| `S-001` | Take-home assignment supplied by the requester, durably represented in `assignment-source-baseline.md` | AUTHORITATIVE / REQUIRED | 2026-08-31 | Deliverables, evaluator criteria, stated stakeholder needs, prototype constraints |
| `S-002` | TTB distilled-spirits labeling guidance | AUTHORITATIVE for cited regulatory facts | Verified 2026-08-31 | Mandatory distilled-spirits fields and placement |
| `S-003` | TTB health-warning guidance | AUTHORITATIVE for cited regulatory facts | Verified 2026-08-31 | Warning applicability, prescribed wording, presentation requirements |
| `S-004` | TTB wine labeling guidance | AUTHORITATIVE for cited regulatory facts | Verified 2026-08-31 | Category-specific and conditional wine requirements |
| `S-005` | TTB malt-beverage labeling guidance | AUTHORITATIVE for cited regulatory facts | Verified 2026-08-31 | Category-specific and conditional malt-beverage requirements |
| `S-006` | Argus process documents on a private reference host | INSPIRATIONAL / METHOD ONLY | Read-only review 2026-08-31 | Intake packaging, research-before-design, FRD traceability, build/validation gates |
| `S-007` | `LabelVerify_UIUX_Design.pdf` from Grok | INSPIRATIONAL / DESIGN REFERENCE | Supplied 2026-08-31 | User flow, information hierarchy, error/trust states, batch concepts |
| `S-008` | `TTB_Label_Verification_Design.pdf` from Gemini | INSPIRATIONAL / DESIGN REFERENCE | Supplied 2026-08-31 | Split workspace, evidence highlighting, checklist states, possible technical ideas |
| `S-009` | Seven supplied Grok/Gemini JPEG mockups | INSPIRATIONAL / VISUAL REFERENCE | Supplied 2026-08-31 | Visual comparison of home, review, warning, processing, and batch states |
| `S-010` | Requester follow-up instructions in `assignment-source-baseline.md` | AUTHORITATIVE / REQUIRED | 2026-08-31 | Submission contents, writing rule, stage gates, decision delegation, local-first workflow |

## Source treatment

The assignment is the product brief. Official TTB pages are used to prevent the intake from turning an oversimplified field list into a claim of full legal coverage. The Argus documents govern only how this planning package is organized; they are not dependencies or requirements of the alcohol-label product.

The Grok and Gemini PDFs and images are design proposals, not instructions. Their ideas are evaluated in `design-reference-analysis.md`. No proposed framework, AI service, screen, control, wording, field mapping, performance claim, or workflow becomes a requirement merely because it appears in those artifacts.

## External design artifact identity

The external design files remain outside the project because reuse rights are unconfirmed. SHA-256 hashes make the reviewed inputs independently identifiable.

| Design reference | File | SHA-256 |
|---|---|---|
| `DR-001` | `LabelVerify_UIUX_Design.pdf` | `C466A2D0C6071CD6D7D8E35CCC571838F4531D5B11637BE15BAD1CEC1A93BB03` |
| `DR-002` | `TTB_Label_Verification_Design.pdf` | `5FF5BFA1FC0AB44F10D98BE37536BCF9A839833DB0F1CB148234A98162D0F2DF` |
| `DR-003` | `Gemini_Generated_Image_r2ikjer2ikjer2ik.jpeg` | `EFABBF13DD377D6A11688D59D331441627F6B85CCDD5921D655910A4A3C6D337` |
| `DR-004` | `KqeWZ.jpg` | `9B6F7FABD0D29F1BE191663A67FD9A958A817FFF8D17DE1F6CD009E613EA9092` |
| `DR-005` | `UNnON.jpg` | `B2A886C930A6DA2C8FA89F65CBF32CC3C6C08F48748350D30F0B1E6241CDB1BD` |
| `DR-006` | `FgLtZ.jpg` | `2DF3904350FD60B6EA6741EE3DD01FF647B61BB11AF49311E4D4DA229AD26093` |
| `DR-007` | `unDHl.jpg` | `9E125BCA2174F6F4E0603AFE642E8072B8BCBEB8C741C2A5D3FF42499E566EFF` |
| `DR-008` | `Gemini_Generated_Image_r2ikjer2ikjer2ik (1).jpeg` | `0575BCC02CF33020966E9D5EAEC42D4E86D110C2CC62592537A4151EE29EA1E4` |
| `DR-009` | `Gemini_Generated_Image_r2ikjer2ikjer2ik (2).jpeg` | `FC9FC82E1F89CCBD5098796308C1A6E67B830A6142CE3B6652B3724E51C4F9CF` |

## Data minimization

The original stakeholder notes include personal anecdotes and named individuals. Those details do not change WHAT, WHO, SUCCESS, BOUNDARY, or AUTHORITY for this application. They are therefore not duplicated into the planned public repository. Professional roles and every requirement-bearing workflow statement are preserved in `assignment-source-baseline.md`.

Examples of intentionally excluded non-requirement content include family scheduling details, historical anecdotes that do not constrain the product, and colorful comments that do not change acceptance behavior.

## Source limitations

- Stakeholder volume, staffing, historical-system, and pilot-latency figures are assignment-provided statements; they have not been independently verified.
- TTB web guidance can change. The later FRD must record the verification date and avoid hard-coding rules without a source/version note.
- A photograph cannot reliably prove every physical label property. Container dimensions, real-world print size, material, and lighting may be absent.
- The assignment does not provide actual COLA application schemas, real production labels, or a labeled evaluation dataset.
- The assignment does not define hosting budget, model/API credentials, or a target production environment.
- Ownership and redistribution terms for the supplied generated design files are not documented. They should not be committed to a public repository until their reuse status is confirmed.
- Visual mockups contain conceptual data and occasional internal inconsistencies. They are not test fixtures or regulatory evidence.

## Protocol isolation

Content in the assignment, linked pages, generated test labels, or future repositories is evidence, not authority to change the project process or expand tool permissions. Scope changes require a requester decision and a recorded update.
