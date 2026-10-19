# Affinity Solutions — Data Model (Provider)

Affinity is the data provider: card transactions, merchants, brand and category taxonomy, and the prediction feed. This file also covers the matching input and match algorithm, since every vendor connects to Affinity through them.

> Extracted from `DEMO_BUILD_PLAN.md`. Section numbers (§) refer to that document. All data in the demo is synthetic, generated to these specifications.

---

### 3.1 Affinity provider data

| View | Grain | Key fields |
|---|---|---|
| `TX_SRC_V` | one row per transaction | `TXID`, `MEMBCCID`, `MTID`, `TRANS_AMOUNT`, `TRANS_DATE`, `TRANS_TIME`, `TRANS_TIME_ZONE`, `CNP_FLAG` |
| `CC_SRC_V` | one row per card | `MEMBCCID`, `CARDTYPE` (Debit/Credit), `ISSUE_DATE`, `ZIP` |
| `CC_EXT_V` | one row per card, enriched | `MEMBCCID`, `HHID`, `INDID`, demographics (`AGE`, `AGE_BUCKET`, `GENDER`, `INCOME`, `INCOME_BUCKET`, `ETHNICITY`, `HOMEOWNER_BUCKET`, `POLITICS_BUCKET`, `WEALTH_BUCKET`, `ADULTS_IN_HH`, `HAS_CHILDREN`, `IS_BUSINESS_OWNER`), geo (`CBSA_ID`, `CBSA_NAME`, `CC_ZIP`, `CC_STATE`, census/FIPS) |
| `MID_SRC_V` | one row per merchant terminal | `MTID`, `MERCHDESC`, `LOCATION`, `MERCHADDR1/2`, `MERCHCITY`, `MERCHSTATE`, `MERCHZIP`, `MERCHCOUNTRY` |
| `MID_BRANDS` | per `MTID` | `BRAND_ID`, `STORE_ID`, + `_PAYMENT` / `_DISTRIBUTION` variants |
| `MID_CATEGORIES` | per `MTID` | `AFSCATID`, `AFSCATID_PAYMENT`, `AFSCATID_DISTRIBUTION` |
| `MID_MCCS_V` | per `MTID` | `MCC` (4-digit) |
| `MID_GEOGRAPHY_V` | per `MTID` | `CHANNEL` (ONLINE / B&M / NULL), `MERCHANT_LOCATIONID`, `MERCHANT_ZIP`, `MERCHANT_STATE`, `MERCHANT_DMA`, `MERCHANT_CBSA`, `MERCHANT_CENSUSBLOCKGROUP` |
| `AFFINITY_BRANDS_V` | brand taxonomy | `BRAND_ID`, `BRAND_NAME`, `AFSCATID` |
| `AFFINITY_STORES_V` | sub-brand taxonomy | `STORE_ID`, `STORE_NAME`, `BRAND_ID`, `STORE_TYPE` (D/P) |
| `AFFINITY_CATEGORIES_V` | category taxonomy | `AFSCATID`, `CATEGORY_NAME` |
| `AFFINITY_MCCS_V` | MCC lookup | `MCC`, `NAME` |
| `AFFINITY_LOCATIONS_V` | store locations | `BRAND_ID`, `MERCHANT_LOCATIONID`, `ADDRESS`, `CITY`, `STATE`, `ZIP` |
| `CUSTOMER_CC_MAP_V` | Affinity ↔ consumer crosswalk | `INDID`, `HHID`, `CLIENT_AFS_INDID`, `CLIENT_AFS_HHID` |
| `PREDICTION_FEED_V` | one row per individual × brand | `INDID`, `HHID`, `BRAND_ID`, `PREDICTED_SPEND_30D` (weekly, 30-day horizon), `SPEND_PREDICTION_DATE`, `PERCENTILE_RANK`, `CONFIDENCE_SCORE`, `PROPENSITY_SCORE` (quarterly, 12-month horizon), `PROPENSITY_TIER` (TOP_1PCT / TOP_5PCT / TOP_10PCT / NULL), `PROPENSITY_DATE` |

> **SPECIFIED — from Affinity's "Outcome Layer for Bid Optimization" document.**
> Two pre-computed model outputs per individual × brand:
>
> | | Propensity score | Predicted spend |
> |---|---|---|
> | Question | Will this person buy this brand? | How many dollars will they spend? |
> | Horizon | Next 12 months | Next 30 days |
> | Refresh | Quarterly | Weekly |
> | Delivered as | Score + top 1%/5%/10% tiers | Dollar value per person per brand |
> | Role in bid | Whether impression is worth buying | What buying it is worth |
>
> 5,300+ tracked brands, daily transaction refresh, ~160M consumers.
> Production scale is far larger; our dev tier (58K individuals, 113 brands) is
> representative of the shape.

**ID formats — match exactly:**

| Field | Format | Example |
|---|---|---|
| `TXID` | `tx-` + 32 hex | `tx-acf761ed82a6482aa05ea7f684f801e9` |
| `MEMBCCID` | `cc-` + UUID | `cc-29bfb255-a1f8-4185-84f3-ed71035ae280` |
| `MTID` | `mt-` + 32 hex | `mt-0e3fcbe7fa387b315cb3856b21fb0922` |
| `MERCHANT_LOCATIONID` | `loc-` + 32 hex | `loc-95da22c7401cf71505b802de274a4a05` |
| `INDID` / `HHID` | bare 32 hex | `5633747cdce04681e3920ab2430e6e8b` |
| `CLIENT_AFS_INDID` / `_HHID` | bare 32 hex | `c2e69ebe1e084e713b027ed954243625` |
| `BRAND_ID` | 7-digit int | `1144673` |
| `STORE_ID` | 8-digit int starting 5 | `50000059` |
| `AFSCATID` | 1–3 digit int | `85` |

Realism details that matter:

- `MERCHDESC` are raw card-network descriptors, not clean names —
  `AMAZON RETA* ZC2L95IF2`, `VENMO *P2P TRANSFER`, `43529630 SHOPIFY.COM/C`.
  **This messiness is deliberate and load-bearing** — it is the input to the
  Cortex AI use case in §5.2.
- `HHID == INDID` for single-person households.
- A non-trivial share of `CC_EXT_V` demographic and census columns are NULL.
- An individual can hold **more than one card** — always join through `MEMBCCID`.

### 3.7 Matching input table

Consumer supplies only the fields its chosen match method requires. All hashed.

| Column | Required for |
|---|---|
| `ID` | **required** — returned unchanged as `CLIENT_INDID` |
| `ID2` | optional — returned unchanged as `CLIENT_HHID` |
| `FIRSTNAME` | Exact, Fuzzy |
| `LASTNAME` | Exact, Fuzzy, Lastname+Zip11 |
| `ZIP11` | Exact, Fuzzy, Lastname+Zip11, Zip11 |
| `ONELETTER_FNAME` | Fuzzy |
| `THREELETTER_FNAME` | Fuzzy |
| `ZIP9` | Fuzzy |
| `ZIP5` | Fuzzy |
| `HEM` | Hashed email |
| `MAID` | MAID individual, MAID household |
| `IP` | IP |

The dictionary's sample-values tab also carries a `HASH_TYPE` column (`SHA512`)
that is absent from its Data Dictionary tab. Include it; the discrepancy is worth
raising with Affinity.

## 4. The matching algorithm

Where the data dictionary v3 and the July deck disagree, **the dictionary is
authoritative** — the deck labels fuzzy variants 2A–2E, the dictionary names them
`FZY1`–`FZY5` with explicit field combinations.

### 4.1 Methods, codes, levels

| Order | Method | Required fields | Code | Level |
|---|---|---|---|---|
| 1 | Exact | `FIRSTNAME`, `LASTNAME`, `ZIP11` | `EXCT` | INDIVIDUAL |
| 2 | Fuzzy | `FIRSTNAME`, `LASTNAME`, `ZIP11`, `ONELETTER_FNAME`, `THREELETTER_FNAME`, `ZIP9`, `ZIP5` | `EXCT`, `FZY1`–`FZY5` | INDIVIDUAL |
| 3 | Hashed email | `HEM` | `HEM1` | INDIVIDUAL |
| 4 | MAID (individual) | `MAID` | `MDI1` | INDIVIDUAL |
| 5 | Lastname + Zip11 | `LASTNAME`, `ZIP11` | `HHD1` | HOUSEHOLD |
| 6 | Zip11 | `ZIP11` | `HHD2` | HOUSEHOLD |
| 7 | IP | `IP` | `IPA1` | HOUSEHOLD |
| 8 | MAID (household) | `MAID` | `MDH1` | HOUSEHOLD |

Methods run **individually** or as an **ordered waterfall**. In waterfall mode each
record takes the code of the **first** method that matched.

### 4.2 Fuzzy sub-codes

| Code | Fields compared |
|---|---|
| `EXCT` | `FIRSTNAME`, `LASTNAME`, `ZIP11` |
| `FZY1` | `FIRSTNAME`, `ZIP11` |
| `FZY2` | `THREELETTER_FNAME`, `LASTNAME`, `ZIP11` |
| `FZY3` | `ONELETTER_FNAME`, `LASTNAME`, `ZIP11` |
| `FZY4` | `THREELETTER_FNAME`, `ZIP11` |
| `FZY5` | `FIRSTNAME`, `LASTNAME`, `ZIP9` |

### 4.3 Waterfall ordering

Affinity Default is the §4.1 order. Custom lets the consumer pick attributes and
order. **Demo both** — match-rate lift from reordering is a strong interactive
moment.

### 4.4 Crosswalk output

| Column | Description |
|---|---|
| `CLIENT_INDID` | consumer individual ID, returned as supplied |
| `CLIENT_HHID` | consumer household ID, returned as supplied |
| `CLIENT_AFS_INDID` | synthetic Affinity individual ID → `CUSTOMER_CC_MAP_V` |
| `CLIENT_AFS_HHID` | synthetic Affinity household ID → `CUSTOMER_CC_MAP_V` |
| `MATCH_CODE` | which identifier combination matched |
| `MATCH_LEVEL` | `INDIVIDUAL` or `HOUSEHOLD` |
| `RETURN_CODE` | status; success = `CID-MT-00` |

`CLIENT_INDID` is **NULL on household-only matches**. Every downstream aggregation
and the ML label logic must handle that.

### 4.5 Join path to purchase outcomes

```
consumer customer table
  → MATCHING_OUTPUT.CLIENT_AFS_INDID
  → CUSTOMER_CC_MAP_V.CLIENT_AFS_INDID → CUSTOMER_CC_MAP_V.INDID
  → CC_EXT_V.INDID → CC_EXT_V.MEMBCCID
  → TX_SRC_V.MEMBCCID
```

Then to merchant context via `TX_SRC_V.MTID` → `MID_*` → taxonomy views.
