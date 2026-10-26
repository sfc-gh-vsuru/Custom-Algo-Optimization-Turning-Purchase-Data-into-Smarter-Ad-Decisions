# Magnite — Data Model (SSP Consumer)

Magnite consumer-side data: the two Exposure Log-Level Data (LLD) feeds, **Streaming** and **DV+**, and their identity mapping. After those come the clean room, ML and demo output tables built on top.

> Source spec: `source_info/MagniteExposureFields_2.2.26.pdf` (Magnite "Gain Granular Exposure Insight from Log Level Data"). All data in the demo is synthetic, generated to these specifications. App, deal and buyer names are fictional. Schema: `AFFINITY_DEMO.MAGNITE_CONSUMER`.

---

### 1. About the feeds

Magnite delivers hourly log-level files (JSON, Avro, Parquet or CSV) to S3, GCS, SFTP or **Snowflake**. Per the spec, buyers use these files to *"validate the audience exposed to their ads and attribute campaign outcomes to ad exposure."*

Key facts that shape the model:

- **Exposure only.** The feeds record that an ad was shown. There is no conversion or purchase field. Affinity purchase outcomes are the **entire** label.
- **No price fields.** Neither feed carries bid, floor or clearing prices. Pricing outputs are therefore *relative multipliers and tiers*, not dollar floors.
- **Mutually exclusive identity (Streaming).** A record carries **either** `IDENTIFIER` + `EID_TYPE` **or** `DEVICE_ID` + `IP_ADDRESS`, never both.
- **DV+ identity** is the extended ID only, with no device ID or IP. DV+ has country only (no DMA or region).

| Table | Rows | Period |
|---|---|---|
| `MAGNITE_STREAMING_LLD` | 6,000,000 | 2026-04-01 → 2026-09-30 |
| `MAGNITE_DVPLUS_LLD` | 4,000,000 | 2026-04-01 → 2026-09-30 |

---

### 2. `MAGNITE_STREAMING_LLD` — Streaming feed (22 fields)

| Column | Spec field | Type | Description / demo values |
|---|---|---|---|
| `IDENTIFIER` | Identifier | VARCHAR | Extended ID value (UID2, RampID, Yahoo ConnectID). NULL when Device ID/IP is sent |
| `EID_TYPE` | EID Type | VARCHAR | `UID2`, `rampID`, `yahoo connect ID` (55% of rows) |
| `DEVICE_ID` | Device ID* | VARCHAR | AAID / IDFA style. Sent in lieu of Identifier (45% of rows) |
| `IP_ADDRESS` | IP Address* | VARCHAR | IPv4 of the ad request. Sent with Device ID |
| `IMPRESSION_TIMESTAMP` | Impression Timestamp | TIMESTAMP_NTZ | Weighted toward evening prime time |
| `DEVICE_MAKE` | Device Make | VARCHAR | e.g. Samsung, LG, Roku, Vizio, Apple |
| `DEVICE_MODEL` | Device Model | VARCHAR | e.g. QN65Q80C, Roku Ultra, Apple TV 4K |
| `DEVICE_OS_NAME` | Device OS Name | VARCHAR | Tizen, webOS, Roku OS, Fire OS, tvOS, iOS, Android… |
| `PLATFORM_FAMILY` | Platform Family | VARCHAR | Connected TV (60%), Mobile, Set Top Box, Game Console, Tablet, Desktop |
| `SUPPLY_DOMAIN` | Supply Domain | VARCHAR | App's domain, e.g. `primeleague.tv` |
| `BUNDLE` | Bundle | VARCHAR | App bundle, e.g. `com.primeleague.sports` (12 streaming apps) |
| `DEAL_ID` | Deal ID | VARCHAR | Magnite deal ID. NULL = open auction |
| `PLAYER_SIZE` | Player Size | VARCHAR | `3840x2160`, `1920x1080`, `1280x720`, `640x480`, `640x360` |
| `DMA` | DMA | VARCHAR | 14 named DMAs + `Other DMA` |
| `REGION` | Region | VARCHAR | US state |
| `COUNTRY` | Country | VARCHAR | `US` |
| `DSP_ID` | DSP ID / Network ID | VARCHAR | Generic, e.g. `DSP-1001` … `DSP-1008` |
| `BUYER_ID` | Buyer ID | VARCHAR | Collection of seats, e.g. `BYR-2001` |
| `BUYER_SEAT_CODE` | Buyer Seat Code | VARCHAR | e.g. `seat-040000` (40 seats) |
| `CREATIVE_ID` | Creative ID | VARCHAR | e.g. `cr-040000-03` |
| `IMPRESSION_ID` | Impression ID | VARCHAR | UUID, unique |
| `AUCTION_ID` | Auction ID | VARCHAR | UUID of the bid request sent to the DSP |

\* IP address and Device ID are available in lieu of Identifier and EID Type. The two groups are never sent together (validated: 0 violations).

---

### 3. `MAGNITE_DVPLUS_LLD` — DV+ feed (17 fields)

| Column | Spec field | Type | Description / demo values |
|---|---|---|---|
| `EXTENDED_ID` | Extended ID | VARCHAR | UID2, RampID or Yahoo ConnectID value (present on 80% of rows) |
| `EXTENDED_ID_SOURCE` | Extended ID Source | VARCHAR | `UID2`, `rampID`, `yahoo connect ID` |
| `TIMESTAMP_` | Timestamp | TIMESTAMP_NTZ | Impression time (daytime-weighted) |
| `COUNTRY` | Country | VARCHAR | `US` (96%), `CA` |
| `DEVICE_TYPE` | Device Type | VARCHAR | Mobile, Desktop, Tablet, Connected TV |
| `DEVICE_OS_NAME` | Device OS Name | VARCHAR | iOS, Android, Windows, macOS, iPadOS, Tizen, webOS |
| `BROWSER_NAME` | Browser Name | VARCHAR | Chrome, Safari, Edge, Firefox, Samsung Internet… |
| `BROWSER_VERSION` | Browser Version | VARCHAR | e.g. `124.0` |
| `BROWSER_LANGUAGE` | Browser Language | VARCHAR | `en-US`, `es-US`, `en-CA`, `fr-CA` |
| `DOMAIN` | Domain | VARCHAR | 15 web/app domains, e.g. `recipebox.com` |
| `FORMAT` | Format | VARCHAR | `display`, `video`, `native` |
| `SIZE_ID` | Size ID / Inventory Specs ID | NUMBER | e.g. 15, 43, 2, 10, 57, 201, 203 |
| `SIZE_NAME` | Size Name / Inventory Specs Name | VARCHAR | e.g. `Medium Rectangle (300x250)`, `Instream Video (640x360)` |
| `CREATIVE_ID` | Creative ID | VARCHAR | Creative returned by the DSP |
| `DEAL_ID` | Deal ID | VARCHAR | Publisher Deal, Marketplace Deal or Auction Package. NULL = open |
| `BUYER_SEAT_TOKEN` | Buyer Seat Token | VARCHAR | Same seat codes as Streaming |
| `IMPRESSION_ID` | Impression ID | VARCHAR | UUID, unique |

---

### 4. Reference tables

| Table | Rows | Columns | Purpose |
|---|---|---|---|
| `MAGNITE_SUPPLY` | 27 | `FEED`, `SUPPLY_NAME`, `BUNDLE`, `SUPPLY_DOMAIN`, `GENRE` | Bundle/domain → readable app/site name + genre |
| `MAGNITE_DEALS` | 16 | `DEAL_ID`, `DEAL_NAME`, `DEAL_TYPE`, `FEED` | Publisher Deals (`MGN-PD-*`), Marketplace Deals (`MGN-MD-*`), Auction Packages (`MGN-AP-*`), Open Auction (`OPEN`) |
| `MAGNITE_BUYERS` | 40 | `DSP_ID`, `BUYER_ID`, `BUYER_SEAT_CODE` | Seat → buyer → DSP hierarchy (generic IDs) |

---

### 5. Identity mapping for Magnite

| Affinity method | Magnite field | Level | Coverage notes |
|---|---|---|---|
| `HEM1` (hashed email) | `IDENTIFIER` / `EXTENDED_ID` where type = `UID2` or `yahoo connect ID` | Individual | Both feeds. Email-based IDs |
| `MDI1` (MAID) | `DEVICE_ID` | Individual | Streaming only (device-mode records) |
| `IPA1` (IP) | `IP_ADDRESS` | Household | Streaming only (device-mode records) |
| RampID | `IDENTIFIER` / `EXTENDED_ID` where type = `rampID` | — | Not resolved in the demo. Needs an ID translation step |

**Note:** Magnite logs have no name, address or postal fields, so the `EXCT`, `FZY*`, `HHD1` and `HHD2` methods do not fire. DV+ can only match on email-based IDs.

#### `MATCHING_INPUT` (920,333 rows)

Distinct identifiers observed across both feeds, submitted to the clean room.

| Column | Type | Description |
|---|---|---|
| `ID_TYPE` | VARCHAR | `UID2`, `rampID`, `yahoo connect ID`, `DEVICE_ID`, `IP_ADDRESS` |
| `ID_VALUE` | VARCHAR | Identifier value |
| `FEEDS` | VARCHAR | `STREAMING`, `DVPLUS` or both |
| `IMPRESSIONS` | NUMBER | Impressions carrying this identifier |

---

### 6. Clean room tables (`AFFINITY_DEMO.CLEANROOM`)

| Table | Rows | Description |
|---|---|---|
| `GROUND_TRUTH_MAGNITE` | 32,000 | Planted overlap: `INDID`, `HHID`, `MAGNITE_USER_ID`, `ASSIGNED_MATCH_CODE`, `ASSIGNED_MATCH_LEVEL` |
| `CROSSWALK_MAGNITE` | 25,847 | Standard crosswalk columns (`AFS_INDID`, `AFS_HHID`, `CLIENT_AFS_INDID`, `CLIENT_AFS_HHID`, `MATCH_CODE`, `MATCH_LEVEL`, `RETURN_CODE`, `WATERFALL_STEP`, `MATCH_DESCRIPTION`, `PLATFORM`, `CLIENT_INDID`, `MATCH_TIMESTAMP`). `CLIENT_INDID` = matched Magnite identifier |
| `MAGNITE_MATCH_RATE_SUMMARY` | 3 | `PLATFORM`, `MATCH_CODE`, `MATCH_LEVEL`, `WATERFALL_STEP`, `MATCHED_COUNT`, `HH_ONLY_COUNT`, `PCT_OF_MATCHED`, `PCT_OF_TOTAL_AFS` |

**Match results (25.8% of Affinity's 100K individuals):**

| Method | Step | Level | Matched | % of Affinity |
|---|---|---|---|---|
| HEM1 | 7 | Individual | 14,463 | 14.5% |
| MDI1 | 8 | Individual | 5,200 | 5.2% |
| IPA1 | 11 | Household | 6,184 (6,111 HH) | 6.2% |

---

### 7. ML tables (`AFFINITY_DEMO.ML`)

#### `TRAINING_SET_MAGNITE` (1,769,069 matched impressions)

| Column | Type | Description |
|---|---|---|
| `IMPRESSION_ID`, `IMP_TIMESTAMP` | VARCHAR, TIMESTAMP | Impression key and time |
| `FEED` | VARCHAR | `STREAMING` / `DVPLUS` |
| `DEVICE_CLASS` | VARCHAR | Platform family (Streaming) or device type (DV+) |
| `DEVICE_OS` | VARCHAR | Device OS name |
| `SUPPLY_NAME` | VARCHAR | App name (via bundle) or domain |
| `AD_FORMAT`, `AD_SIZE` | VARCHAR | Format and player size / size name |
| `DEAL_ID`, `DEAL_TYPE` | VARCHAR | Deal (`OPEN` for open auction) and type |
| `DMA`, `REGION`, `COUNTRY` | VARCHAR | Geo (`Not provided` for DV+) |
| `DSP_ID`, `BUYER_SEAT_CODE` | VARCHAR | Winning buyer |
| `ID_TYPE_USED`, `MATCH_CODE` | VARCHAR | Identifier on the record and Affinity match method |
| `AFS_INDID`, `AFS_HHID` | VARCHAR | Affinity individual / household (clean room only) |
| `DAYPART` | VARCHAR | Morning / Afternoon / Evening / LateNight |
| `CROSS_SCREEN` | NUMBER | 1 = person matched on both feeds |
| `AFFINITY_PROPENSITY` | NUMBER | Affinity purchase score for the individual |
| `COMPOSITE_PROPENSITY` | NUMBER | Generation-time purchase probability (not a model feature) |
| `PURCHASED` | NUMBER | Label: 1 = purchase followed (1.09% overall; Streaming 1.28%, DV+ 0.71%) |
| `PURCHASE_AMOUNT`, `PURCHASE_TX_COUNT` | NUMBER | Purchase value (avg $104, median $72) and transactions |
| `SPEND_TIER` | VARCHAR | `HIGH` (≥$200) / `MID` ($75–200) / `LOW` / `NONE` |
| `IS_HOLDOUT` | NUMBER | 1 = 20% holdout, never used in training |
| `PLATFORM` | VARCHAR | `MAGNITE` |

#### Models and results

| Object | Description |
|---|---|
| `MAGNITE_YIELD_CLASSIFIER` | `SNOWFLAKE.ML.CLASSIFICATION` on `PURCHASED`. 13 features. AUC 0.762 |
| `MAGNITE_SPEND_CLASSIFIER` | `SNOWFLAKE.ML.CLASSIFICATION` on `SPEND_TIER`. 13 features. AUC 0.758 |
| `MAGNITE_TRAIN_INPUT` | 80% training rows used to fit both models (permanent table) |
| `MAGNITE_YIELD_PREDICTIONS` | Holdout rows + `PREDICTION` variant (353,369 rows) |
| `MAGNITE_VALIDATION_DECILES` | `DECILE`, `TOTAL`, `PURCHASERS`, `PURCHASE_RATE_PCT`, `PCT_OF_ALL_PURCHASES`, `CUMUL_CAPTURE_PCT`, `DECILE_LIFT`. Top decile 3.9x; top 30% = 69% of purchases |
| `MAGNITE_FEATURE_IMPORTANCE` | `MODEL`, `RANK`, `FEATURE`, `IMPORTANCE_SCORE` for both models |
| `MAGNITE_HOLDOUT_RESULTS` | `SET_NAME`, `IMPRESSIONS`, `PURCHASES`, `PURCHASE_RATE_PCT`, `AVG_PURCHASE_VALUE`, `VALUE_PER_1K_IMPS`. Training vs holdout, plus holdout top 30% vs remaining 70% |
| `MODEL_REGISTRY` | Two `MAGNITE_*` rows added |

**Model features (decision-time + Affinity score):** `FEED`, `DEVICE_CLASS`, `DEVICE_OS`, `SUPPLY_NAME`, `AD_FORMAT`, `AD_SIZE`, `DEAL_TYPE`, `DMA`, `DAYPART`, `MATCH_CODE`, `BUYER_SEAT_CODE`, `CROSS_SCREEN`, `AFFINITY_PROPENSITY`.

---

### 8. Demo output tables (`MAGNITE_CONSUMER`)

| Table | Rows | Columns | Dashboard tab |
|---|---|---|---|
| `DEMO_OUTPUT_IDENTITY_COVERAGE` | 8 | `FEED`, `ID_TYPE`, `IMPRESSIONS`, `MATCHED_IMPRESSIONS`, `MATCH_RATE_PCT`, `HOW_AFFINITY_MATCHES` | Identity Coverage |
| `DEMO_OUTPUT_MATCH_SUMMARY` | 3 | Copy of `CLEANROOM.MAGNITE_MATCH_RATE_SUMMARY` | Identity Coverage |
| `DEMO_OUTPUT_SUPPLY_YIELD` | 2,880 | `FEED`, `SUPPLY_NAME`, `GENRE`, `DEVICE_CLASS`, `AD_SIZE`, `DAYPART`, `MATCHED_IMPRESSIONS`, `PURCHASES`, `PURCHASE_RATE_PCT`, `YIELD_INDEX`, `PURCHASE_VALUE`, `VALUE_PER_1K_IMPS` | CTV Yield |
| `DEMO_OUTPUT_DEAL_OUTCOMES` | 16 | `DEAL_ID`, `DEAL_NAME`, `DEAL_TYPE`, `FEED`, `TOTAL_IMPRESSIONS`, `MATCHED_IMPRESSIONS`, `MATCHED_INDIVIDUALS`, `PURCHASES`, `PURCHASE_RATE_PCT`, `YIELD_INDEX`, `AVG_PURCHASE_VALUE`, `VALUE_PER_1K_IMPS`, `OUTCOME_GRADE` (A–D) | Verified Deals |
| `DEMO_OUTPUT_CURATED_PACKAGES` | 7 | `PACKAGE_NAME`, `DESCRIPTION`, `FEEDS`, `MATCHED_IMPRESSIONS`, `REACH_INDIVIDUALS`, `REACH_HOUSEHOLDS`, `PURCHASES`, `PURCHASE_RATE_PCT`, `LIFT_VS_AVG`, `AVG_PURCHASE_VALUE`, `VALUE_PER_1K_IMPS`, `SUGGESTED_PRICE_TIER` | Verified Deals + Packages |
| `DEMO_OUTPUT_BUYER_OUTCOMES` | 40 | `DSP_ID`, `BUYER_ID`, `BUYER_SEAT_CODE`, `IMPRESSIONS_WON`, `CTV_SHARE_PCT`, `MATCHED_IMPRESSIONS`, `PURCHASES`, `PURCHASERS`, `PURCHASE_RATE_PCT`, `LIFT_VS_AVG`, `ATTRIBUTED_PURCHASE_VALUE`, `VALUE_PER_1K_IMPS`, `BEST_SUPPLY`, `OUTCOME_STATUS` | Buyer Outcomes |
| `DEMO_OUTPUT_PRICING_RULES` | 535 | `RULE_ID`, `PREDICATE`, `DIM`, `DIM_VALUE`, `SUPPORT`, `PURCHASE_RATE`, `BASELINE_RATE`, `RAW_LIFT`, `SHRUNK_LIFT`, `PRICE_MULTIPLIER`, `CI_LOWER`, `CI_UPPER`, `RULE_ACTION` (103 BOOST / 163 NEUTRAL / 269 SUPPRESS), `SOURCE_PLATFORM`, `VALID_FROM`, `VALID_TO` | Pricing Rules |
| `DEMO_OUTPUT_PRICING_TIERS` | 131 | `FEED`, `SUPPLY_NAME`, `DEVICE_CLASS`, `MATCHED_IMPRESSIONS`, `PURCHASES`, `PURCHASE_RATE_PCT`, `YIELD_INDEX`, `VALUE_PER_1K_IMPS`, `PRICE_TIER` (Premium / Plus / Standard / Value), `SUGGESTED_PRICE_MULTIPLIER` | Pricing Rules |
| `DEMO_OUTPUT_CROSS_SCREEN` | 6 | `LEVEL` (Individual / Household), `EXPOSURE_GROUP` (CTV only / Display only / CTV + Display), `UNITS`, `IMPRESSIONS`, `IMPS_PER_UNIT`, `PURCHASES`, `PURCHASE_RATE_PCT`, `CTV_PURCHASE_RATE_PCT`, `DISPLAY_PURCHASE_RATE_PCT`, `CTV_LIFT_VS_SINGLE_SCREEN`, `DISPLAY_LIFT_VS_SINGLE_SCREEN`, `PCT_UNITS_PURCHASING`, `AVG_PURCHASE_VALUE` | Cross-Screen |

**Rule-building notes:**
- Rules use only fields known when the impression is sold: feed, device, supply, size, deal type, DMA, daypart, OS, format, and pairs of these. Buyer seat, match code and Affinity score are excluded.
- Minimum support is 2,000 training impressions.
- Lift is shrunk toward 1.0 with a 5,000-impression prior, and 95% confidence intervals are computed.
- BOOST = shrunk lift ≥ 1.15 and CI lower bound > 1. SUPPRESS = shrunk lift ≤ 0.85 and CI upper bound < 1.
