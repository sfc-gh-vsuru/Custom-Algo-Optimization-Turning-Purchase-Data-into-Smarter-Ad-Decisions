# AdRoll / NextRoll — Data Model (Retargeting DSP Consumer)

AdRoll consumer-side data: Granular Conversion Report, server-to-server events, campaign metrics, Site Traffic Revealer (B2B), and identity mapping. Followed by the demo output and ML validation tables.

> Extracted from `DEMO_BUILD_PLAN.md`. Section numbers (§) refer to that document. All data in the demo is synthetic, generated to these specifications.

---

### 3.5 AdRoll consumer data (retargeting DSP) — conversion-scoped, not impression-scoped

AdRoll/NextRoll is a retargeting DSP. AdRoll's primary data export is **conversion-scoped** — the
Granular Conversion Report (GCR). Impression-level log data is not publicly
available from AdRoll's API. This is a deliberate design choice by NextRoll and
shapes the entire AdRoll demo around conversions, funnel events, and B2B signals.

#### 3.5.1 Granular Conversion Report (GCR)

The GCR is AdRoll's primary analytics export. Schema from `apidocs.nextroll.com`
GraphQL Reporting API.

| Column | Type | Description |
|---|---|---|
| `CONVERSION_ID` | VARCHAR | Unique conversion event ID |
| `CONVERSION_TIMESTAMP` | TIMESTAMP | When the conversion occurred |
| `EMAIL_SHA256` | VARCHAR | SHA-256 hashed email — **primary match key** |
| `ADVERTISER_EID` | VARCHAR | AdRoll advertiser entity ID |
| `CAMPAIGN_EID` | VARCHAR | Campaign entity ID |
| `CAMPAIGN_NAME` | VARCHAR | Campaign display name |
| `ADGROUP_EID` | VARCHAR | Ad group entity ID |
| `ADGROUP_NAME` | VARCHAR | Ad group display name |
| `AD_EID` | VARCHAR | Ad entity ID |
| `AD_NAME` | VARCHAR | Ad display name |
| `CHANNEL` | VARCHAR | `web`, `social`, `email`, `native`, `display`, `video`, `ctv` |
| `DEVICE_TYPE` | VARCHAR | `desktop`, `mobile`, `tablet`, `ctv`, `other` |
| `GEO_COUNTRY` | VARCHAR | Country code |
| `GEO_REGION` | VARCHAR | State/region |
| `GEO_CITY` | VARCHAR | City |
| `GEO_DMA` | VARCHAR | Nielsen DMA |
| `ATTRIBUTED_REVENUE` | FLOAT | Pixel-reported conversion value ($) |
| `ATTRIBUTION_TYPE` | VARCHAR | `click_through`, `view_through` |
| `ATTRIBUTION_WINDOW_DAYS` | INTEGER | 1, 7, 14, or 28 days |
| `CONVERSION_TYPE` | VARCHAR | `purchase`, `signup`, `lead`, `addToCart`, `pageView` |
| `LANDING_PAGE_URL` | VARCHAR | Destination URL |
| `REFERRER_URL` | VARCHAR | Referring URL |
| `OS` | VARCHAR | Operating system |
| `BROWSER` | VARCHAR | Browser name |
| `IP_ADDRESS` | VARCHAR | Device IP address |
| `USER_AGENT` | VARCHAR | Full user agent string |
| `IS_NEW_VISITOR` | BOOLEAN | First-time vs returning visitor |
| `SESSION_DURATION_SEC` | INTEGER | Session length in seconds |

**Key design point:** The GCR is conversion-scoped,
not impression-scoped. Each row represents a conversion event, not an ad impression.
This means the ML layer works on conversions (verifying which are real purchases)
rather than on impressions (predicting which will lead to purchases).

#### 3.5.2 Server-to-Server (S2S) Events

AdRoll's S2S Event API tracks 13 event types across the full marketing funnel.
Schema from `apidocs.nextroll.com`.

| Column | Type | Description |
|---|---|---|
| `EVENT_ID` | VARCHAR | Unique event ID |
| `EVENT_TIMESTAMP` | TIMESTAMP | When the event occurred |
| `EVENT_TYPE` | VARCHAR | One of 13 types (see below) |
| `EMAIL_SHA256` | VARCHAR | SHA-256 hashed email |
| `ADVERTISER_EID` | VARCHAR | AdRoll advertiser entity ID |
| `SESSION_ID` | VARCHAR | Session tracking ID |
| `DEVICE_TYPE` | VARCHAR | Device category |
| `CHANNEL` | VARCHAR | Marketing channel |
| `GEO_COUNTRY` | VARCHAR | Country code |
| `GEO_REGION` | VARCHAR | State/region |
| `GEO_CITY` | VARCHAR | City |
| `GEO_DMA` | VARCHAR | Nielsen DMA |
| `IP_ADDRESS` | VARCHAR | Device IP |
| `PAGE_URL` | VARCHAR | Page URL |
| `REFERRER_URL` | VARCHAR | Referring URL |
| `PRODUCT_ID` | VARCHAR | Product identifier (for commerce events) |
| `PRODUCT_NAME` | VARCHAR | Product name |
| `PRODUCT_PRICE` | FLOAT | Product price |
| `QUANTITY` | INTEGER | Product quantity |

**13 event types:**
`pageView`, `productView`, `productSearch`, `addToCart`, `removeFromCart`,
`startCheckout`, `purchase`, `signup`, `login`, `demoRequest`, `contactSales`,
`signupTrial`, `custom`

**B2C events:** pageView → productSearch → productView → addToCart → startCheckout → purchase
**B2B events:** pageView → demoRequest / contactSales / signupTrial

#### 3.5.3 Campaign Metrics

Aggregated campaign performance data from AdRoll's GraphQL Reporting API.

| Column | Type | Description |
|---|---|---|
| `DATE` | DATE | Reporting date |
| `CAMPAIGN_EID` | VARCHAR | Campaign entity ID |
| `CAMPAIGN_NAME` | VARCHAR | Campaign display name |
| `CAMPAIGN_TYPE` | VARCHAR | `retargeting`, `brand_awareness`, `prospecting` |
| `ADGROUP_EID` | VARCHAR | Ad group entity ID |
| `CHANNEL` | VARCHAR | Marketing channel |
| `DEVICE_TYPE` | VARCHAR | Device category |
| `IMPRESSIONS` | INTEGER | Impressions served |
| `CLICKS` | INTEGER | Clicks recorded |
| `CTR` | FLOAT | Click-through rate |
| `SPEND` | FLOAT | Ad spend ($) |
| `CONVERSIONS` | INTEGER | Attributed conversions |
| `ATTRIBUTED_REVENUE` | FLOAT | Pixel-reported revenue |
| `CPA` | FLOAT | Cost per acquisition |
| `ROAS` | FLOAT | Return on ad spend |
| `VIDEO_COMPLETIONS` | INTEGER | Video completions (CTV/video campaigns) |
| `VIDEO_COMPLETION_RATE` | FLOAT | Video completion rate |

#### 3.5.4 Site Traffic Revealer (B2B firmographics)

AdRoll's unique B2B capability — identifies companies visiting the advertiser's
website using reverse IP lookup and firmographic databases. Schema from
`apidocs.nextroll.com`.

| Column | Type | Description |
|---|---|---|
| `DOMAIN` | VARCHAR | Company domain |
| `COMPANY_NAME` | VARCHAR | Company display name |
| `COMPANY_INDUSTRY` | VARCHAR | Industry vertical (~150 values: Technology, Healthcare, Finance, etc.) |
| `COMPANY_REVENUE` | VARCHAR | Revenue bucket: `<$1M`, `$1M-$10M`, `$10M-$50M`, `$50M-$100M`, `$100M-$500M`, `$500M-$1B`, `>$1B` |
| `COMPANY_SIZE` | VARCHAR | Employee count bucket: `1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `>10000` |
| `JOURNEY_STAGE` | VARCHAR | ABM funnel stage: `Unaware`, `Aware`, `Engaged`, `MQL`, `Opportunity` |
| `FIRST_VISIT_DATE` | DATE | First recorded visit |
| `TOTAL_VISITS` | INTEGER | Total site visits |
| `TOTAL_VISITORS` | INTEGER | Unique visitors |
| `CONTACT_EMAIL_SHA256` | VARCHAR | SHA-256 hashed contact email (when available) |

**What makes this unique:** Site Traffic Revealer provides B2B firmographic
data on site visitors. This enables a completely new use case — scoring
companies by actual purchase propensity rather than just web engagement.

#### 3.5.5 Identity mapping for AdRoll

| Affinity method | AdRoll field | Coverage notes |
|---|---|---|
| `HEM1` (hashed email) | `EMAIL_SHA256` in GCR + S2S | **Primary.** Deterministic, highest confidence. Present on ~80% of conversions. |
| `IPA1` (IP) | `IP_ADDRESS` | Fallback for non-logged-in events |

**No MAID, no name/address, no RampID.** AdRoll identity is email-centric.
`HEM1` alone produces an 80.6% match rate against Affinity's base, because
email SHA-256 is deterministic (not probabilistic like IP or device graph).

#### 3.5.6 What makes AdRoll data distinctive

- **Conversion-scoped, not impression-scoped** — ML works on "which conversions
  are real purchases" rather than "which impressions lead to purchases." Different
  question, different model architecture.
- **Email SHA-256 as primary identity** — deterministic matching. No graph
  resolution, no probabilistic decay.
- **Full-funnel S2S events** — 13 typed events from pageView through purchase,
  including B2B signals (demoRequest, contactSales, signupTrial). Enables funnel
  intelligence rules.
- **B2B firmographics** — Site Traffic Revealer is unique to AdRoll. Industry,
  revenue, headcount, journey stage on 5,000+ companies. Combined with Affinity
  purchase data, this powers account-level scoring.
- **No impression-level data** — AdRoll does not provide impression-level log
  streams publicly.
  The demo uses conversion-level and campaign-aggregate data per documented API schemas.
- **CTV attribution via campaign metrics** — CTV campaigns are attributed through
  matched conversion events, not impression logs. Video completion rates and ROAS
  are derived from campaign-level aggregates.

---

### Demo output tables (§5A.4)

#### Output schema (`ADROLL_CONSUMER` + `ADROLL_B2B`)

| Table | Schema | Description |
|---|---|---|
| `ADROLL_FUNNEL_PURCHASE_RULES` | `ADROLL_CONSUMER` | 120 ML-derived rules: `RULE_ID`, `PREDICATE`, `DIM`, `DIM_VALUE`, `SUPPORT`, `PURCHASE_RATE`, `RAW_LIFT`, `SHRUNK_LIFT`, `BID_MULTIPLIER`, `CI_LOWER/UPPER`, `RULE_ACTION` (BOOST/NEUTRAL/SUPPRESS) |
| `ADROLL_CHANNEL_ATTRIBUTION` | `ADROLL_CONSUMER` | Per channel: `CHANNEL`, `CONVERSIONS`, `PIXEL_REVENUE`, `CARD_SWIPE_REVENUE`, `REVENUE_DELTA_PCT`, `VERIFIED_PURCHASES`, `TRUE_PURCHASE_RATE_PCT` |
| `ADROLL_CTV_ATTRIBUTION` | `ADROLL_CONSUMER` | 50 CTV campaigns: `CAMPAIGN_NAME`, `VIDEO_IMPRESSIONS`, `VIDEO_COMPLETIONS`, `CTV_SPEND`, `MATCHED_PURCHASERS`, `TOTAL_PURCHASE_VALUE`, `CTV_ROAS`, `COMPLETION_TO_PURCHASE_RATE` |
| `ADROLL_AUDIENCE_SEGMENTS` | `ADROLL_CONSUMER` | Audience segments: `SEGMENT_EID`, `SEGMENT_NAME`, `SEGMENT_TYPE`, `DURATION`, `IS_CONVERSION`, `CONVERSION_VALUE`, `ESTIMATED_SIZE` |
| `ADROLL_ACCOUNT_SCORES` | `ADROLL_B2B` | 5,000 B2B accounts: `DOMAIN`, `COMPANY_NAME`, `COMPANY_INDUSTRY`, `COMPANY_REVENUE`, `COMPANY_SIZE`, `JOURNEY_STAGE`, `TOTAL_VISITS`, `PURCHASE_SCORE`, `PREDICTED_ACCOUNT_VALUE`, `SCORE_TIER` (HOT/WARM/COLD) |
| `ADROLL_SITE_TRAFFIC_REVEALER` | `ADROLL_B2B` | Raw firmographic data: 10 fields per company including `CONTACT_EMAIL_SHA256` for Affinity matching |

#### ML validation tables

| Table | Schema | Description |
|---|---|---|
| `ADROLL_CONVERSION_DECILES` | `ML` | 10 decile bins with purchase rate and lift. Top decile: 3.22x lift. |
| `ADROLL_FEATURE_IMPORTANCE` | `ML` | Feature importance for Conversion Classifier and Funnel Predictor side-by-side. Conversion: ATTRIBUTED_REVENUE #1. Funnel: COMPOSITE_PROPENSITY #1. |
| `ADROLL_HOLDOUT_RESULTS` | `ML` | Training vs holdout: purchase rate, revenue, conversion counts. Confirms model generalizes. |
