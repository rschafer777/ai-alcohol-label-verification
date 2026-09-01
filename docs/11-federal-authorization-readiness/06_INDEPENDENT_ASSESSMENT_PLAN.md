# Independent Assessment Plan

Artifact status: OPEN  
Official sources retrieved: 2026-09-01  
FedRAMP Recognized independent assessment service: PENDING  
Assessment class and scope: PENDING

## 1. Objective

Prepare a FedRAMP Recognized independent assessment service to verify that documented measures are implemented and validate that they produce the intended outcomes across the effective Minimum Assessment Scope. For Class B or Class C, plan for all applicable KSIs to be included in an independent assessment at least annually.

## 2. Entry criteria

- [ ] Provider legal entity and accountable official established
- [ ] Federal use case, scope determination, and certification class established
- [ ] Effective Minimum Assessment Scope and third-party resources documented
- [ ] Production environment operational with stable sources of truth
- [ ] CPO, SDR, SCG, KSI inventory, responsibility matrix, and risk register current
- [ ] Internal verification and validation complete for every applicable rule and KSI
- [ ] Persistent metrics and vulnerability history meet the selected-class preparation needs
- [ ] Sensitive evidence access method approved
- [ ] Open risks have owners, decisions, and target dates

## 3. Assessor selection

| Criterion | Required evidence | Status |
|---|---|---|
| FedRAMP Recognition | Current FedRAMP Marketplace listing and assessor ID | PENDING |
| Applicable capability | Experience with 20x, selected class, architecture, cloud, and automation model | PENDING |
| Independence | Conflict-of-interest and objectivity review | PENDING |
| Technical depth | Ability to review effective configuration, code where appropriate, automation, metrics, and outcomes | PENDING |
| Evidence security | Approved handling, access, retention, personnel, and destruction terms | PENDING |
| Schedule and capacity | Initial and annual assessment milestones | PENDING |
| Findings process | Severity, dispute, correction, retest, and final-summary method | PENDING |

## 4. Assessment work packages

| Work package | Provider supplies | Assessor activity | Exit evidence |
|---|---|---|---|
| Scope confirmation | Resource inventory, flows, categories, third parties, interfaces, exclusions | Verify the scope includes all resources likely to handle or affect federal customer data | Approved assessed inventory and scope comments |
| Package review | Current CPO, SDR, SCG, KSI records, metrics, risks | Check completeness, clarity, current state, and internal verification and validation | Package review findings |
| Technical implementation | IaC, cloud configuration, identity, code, build, runtime, network, crypto, logs, backup, vulnerability and change sources | Inspect actual measures, not only prose or screenshots | Implementation verification record |
| Effectiveness validation | Test plans, safe inputs, historical metrics, alerts, exercises, incident and recovery records | Independently validate intended outcomes | Validation results and exceptions |
| Automation review | Generators, sensors, source integrity, coverage, failure behavior | Verify automation accuracy, completeness, and resistance to silent gaps | Automation assessment results |
| KSI assessment | Complete KSI inventory and evidence | Assess all applicable KSIs for selected class | KSI conclusions |
| Risk and correction | Risk register, accepted risks, remediation evidence | Review weaknesses, disputes, corrective actions, and retests | Final open-risk set and retest results |
| Package inclusion | Final assessor materials | Confirm assessment results are included without inappropriate modification | Assessor confirmation and overall summary |

## 5. Evidence room structure

| Collection | Content | Access status |
|---|---|---|
| Public | CPO public fields, service list, SCG, contacts, report dates | PENDING trust center |
| Controlled provider package | SDR, detailed architecture, KSI evidence, metrics, policies, procedures, risk records | PENDING |
| Sensitive technical evidence | Cloud exports, security logs, vulnerability detail, identity and key evidence, incident materials | PENDING restricted method |
| Independent assessment | Test plans, procedures, results, disputes, summary, provider responses | PENDING assessor repository |
| Agency handoff | Reusable provider evidence plus agency responsibility statements | PENDING agency access |

## 6. Test rules

- Use representative samples only when justified and document the sampling rationale.
- Prefer direct technical observation of source-of-truth configuration and persistent validation results.
- Record expected and observed outcomes, environment, effective resources, time, operator, and evidence location.
- Preserve failed and disputed results and link corrective actions.
- Do not use production federal customer content to create unsafe tests.
- Reassess corrective changes and any scope impact before final assessment closure.

## 7. Milestones

| Milestone | Target | Status |
|---|---|---|
| Readiness and evidence-gap workshop | PENDING program approval | PENDING |
| Assessor selected and conflict review complete | PENDING | PENDING |
| Scope and assessment plan agreed | PENDING | PENDING |
| Initial technical evidence collection complete | PENDING | PENDING |
| Independent testing complete | PENDING | PENDING |
| Findings corrected or risk dispositioned | PENDING | PENDING |
| Final assessment summary included in package | PENDING | PENDING |
| Annual reassessment cycle scheduled | PENDING | PENDING |

## 8. Official basis

- [FedRAMP Independent Verification and Validation](https://www.fedramp.gov/2026/providers/20x/rules/independent-verification-and-validation/)
- [FedRAMP Marketplace assessors](https://www.fedramp.gov/marketplace/assessors/)
- [NIST SP 800-53A Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final)
