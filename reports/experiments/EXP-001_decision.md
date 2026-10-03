# EXP-001 - Free-shipping progress bar on cart
**Decision: SHIP WITH MONITORING**  
conversion_rate +14.5% (95% CI +8.7% to +20.5%), P(better)=100.0%, expected loss 0.00%. Guardrails at risk: refund_rate - monitor post-launch.

> Data is SIMULATED for portfolio demonstration.

| Platform | Owner | Window | Planned n/arm | Actual n (C / T) |
|---|---|---|---|---|
| Nykaa | Growth / Checkout | 2025-03-03 to 2025-03-30 | 70,229 (28 days) | 76,013 / 75,987 |

**Hypothesis:** Showing "You're Rs.X away from free shipping" on the cart page will increase checkout conversion because it reduces surprise shipping costs.

## 1. Validity
SRM chi-square p = 9.47e-01 -> passed (observed split {'control': 0.5001, 'treatment': 0.4999})

## 2. Metrics
| Role | Metric | Control | Treatment | Rel. lift | 95% CI | p | P(T better) | Status |
|---|---|---|---|---|---|---|---|---|
| primary | conversion_rate | 0.0346 | 0.0397 | +14.47% | +8.75% to +20.50% | 0.0000 | 100.0% | - |
| secondary | revenue_per_user | 22.1139 | 25.5181 | +15.39% | +8.87% to +21.91% | 0.0000 | 100.0% | - |
| guardrail | gross_margin_per_user | 6.6342 | 7.6554 | +15.39% | +8.87% to +21.91% | 0.0000 | 100.0% | OK |
| guardrail | refund_rate | 0.0596 | 0.0551 | -7.60% | -25.24% to +14.20% | 0.4644 | 23.1% | AT RISK |

CUPED (pre-period revenue) cut variance on revenue metrics by ~2%.

## 3. Business impact (annualised on eligible traffic)
- Revenue: Rs.7,455,281
- Gross margin: Rs.2,236,589

## 4. Segment cuts (exploratory, Holm-adjusted)
| Segment | Lift | 95% CI | p (Holm) |
|---|---|---|---|
| College Students | +8.93% | -2.97% to +22.29% | 0.147 |
| Premium Shoppers | +12.65% | +0.60% to +26.15% | 0.117 |
| Tier 2 City Customers | +12.68% | +0.34% to +26.54% | 0.117 |
| Working Women | +19.29% | +6.54% to +33.56% | 0.011 |
| Youth | +18.99% | +5.96% to +33.63% | 0.013 |

Segment results are for generating the next hypothesis only - the decision uses the pre-registered primary metric and guardrails.