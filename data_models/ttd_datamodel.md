# The Trade Desk (TTD) — Data Model (DSP Consumer)

TTD consumer-side data: advertiser CRM, identity spine, and REDS impression and conversion feeds. Followed by the demo output tables built on top.

> Extracted from `DEMO_BUILD_PLAN.md`. Section numbers (§) refer to that document. All data in the demo is synthetic, generated to these specifications.

---

### 3.2 TTD consumer data (DSP) — three parts, not one

TTD's REDS is fully specified from TTD's published documentation, and TTD's own
sample data workbook is saved locally as `REDS_sample_data.xlsx`. Seed generator
distributions from that file rather than inventing value formats.

#### 3.2.1 The identity constraint that drives this design

REDS carries **exactly one identifier per event**, as a column trio:

| Column | Meaning | Example |
|---|---|---|
| `CombinedIdentifier` | the ID string — one per event, never a composite | `RDNcJKezWx2xwzd8YjWZ7KPax/fBH12ORMHxqGH5YDU=` |
| `CombinedIdentifierType` | `TDID`, `DAID`, `RampID`, `RawUID2`, `UID2Token`, `EUID`, `RawEUID` | `UID2` |
| `CombinedIdentifierForm` | `Originating` \| `Legacy` \| `Removed: Restriction` \| `Hashed: Restriction` | `Originating` |

Checked against the eight Affinity match methods:

| Affinity method | Needs | In REDS? |
|---|---|---|
| Exact / Fuzzy (`EXCT`, `FZY1–5`) | name + `ZIP11` | ❌ no name fields at all |
| Hashed email (`HEM1`) | `HEM` | ❌ no email. `RawUID2` is a *salted* hash — not an Affinity HEM |
| MAID individual / household (`MDI1`, `MDH1`) | `MAID` | ⚠️ only where type is `DAID` |
| Lastname + Zip11 (`HHD1`) | `LASTNAME`, `ZIP11` | ❌ no lastname |
| Zip11 household (`HHD2`) | `ZIP11` | ❌ `Zip` is 5-digit — ZIP11 ≠ ZIP5 |
| IP household (`IPA1`) | `IP` | ✅ `IPAddress` |

**An impression log cannot be the matching input.** At most three of eight methods
would fire, and only `IPA1` on every row.

So the consumer side has three datasets, which is also the correct real-world
design:

```
  Advertiser 1P CRM  ──►  match waterfall (all 8 methods)
  (name, email, addr)        └─► CLIENT_AFS_INDID / CLIENT_AFS_HHID
        │
        │ identity spine: CRM key ↔ TDID / DAID / UID2 / RampID
        ▼
  REDS Impressions  ──►  joined on CombinedIdentifier
  (bid-time features)
```

This is exactly what TTD's Originating ID feature exists to support — per TTD,
OGIDs *"eliminate graph cross-walking, increasing match rates and conversion
coverage."* Showing `Originating` vs `Legacy` match rates is a natural demo beat.

#### 3.2.2 Advertiser CRM

The matching input. Name, address, email, MAID, at the coverage mix agreed at the
§6 checkpoint. Feeds the waterfall; hashed per the Affinity matching input table (§3.7).

#### 3.2.3 Identity spine

CRM key ↔ `CombinedIdentifier`, with `CombinedIdentifierType` and
`CombinedIdentifierForm` populated to a realistic channel mix — CTV and in-app
skew `DAID`, web skews `TDID`, logged-in inventory skews `UID2`. Deliberate gaps
here are what force `IPA1` fallback and make the waterfall visibly necessary.

#### 3.2.4 REDS Impressions — the ML feature space

Generate to TTD's **current 3-0-0 column names**. Load TTD's enum tables (`OS`
101–268, `Browser` 1–15, `DeviceType` 1–8, `OSFamily` 1–7, `InventoryChannel` 0–7,
`AudioFeedId` 1–7, `ContentDuration` bands, `TTDNativeContextTypeId`,
`UserHourOfWeek` 0–167) into `UTIL` as generator lookups.

**Keys / hierarchy** — `LogEntryTime`, `ImpressionId`, `PartnerId`,
`AdvertiserId`, `CampaignId`, `AdGroupId`, `CreativeId`, `AudienceId`,
`PrivateContractId`, plus `*IdInteger` variants

**Supply path** — `SupplyVendorId`, `SupplyVendorName`, `SupplyVendorPublisherId`,
`DealId`, `Site`, `ImpressionPlacementId` (GPID), `AdsTxtSellerType`,
`AuctionType`, `SupplyType` (`OpenPath` = publisher-direct), `SellingParty*`

**Creative / channel** — `AdFormat`, `InventoryChannel`, `RenderingContext`,
`NativePlacementTypeId`, `TTDNativeContextTypeId`

**Device** — `DeviceType`, `OSFamily`, `OS`, `Browser`, `DeviceMake`,
`DeviceModel`, `UserAgent`, `Carrier`

**Geo** — `IPAddress`, `Zip` (5-digit), `City`, `Region`, `CountryLong`,
`NielsenDMA`, `Latitude` / `Longitude` (2dp)

**Time** — `UserHourOfWeek`, 0–167, encoding day × hour in the *user's* timezone.
Use it directly; do not invent separate daypart columns.

**Economics** — `MediaCostInBucks`, `FeeFeaturesCost`, `DataUsageTotalCost`,
`TTDCostInUSDollars`, `PartnerCostInUSDollars`, `AdvertiserCostInUSDollars`, plus
currency and FX columns

**Content / CTV** — `ContentGenre1`–`5`, `MatchedGenre`, `ContentRating`,
`ContentNetwork`, `ContentChannel`, `ContentDuration`,
`ContentProductionQuality`, `LiveStream`, `TVQualityIndex` (1–100),
`AudioFeedId`, `AudioContentSeries`

**Targeting signal** — `Recency` (minutes since user seen on targeted element),
`ReferrerCategories`, `MatchedLanguageCode`, `AudienceUnlimitedTierName`

Do not generate `TradingModeName` or `ImpressionCostInUSDollars` — both deprecated
and always null. Skip the third-party viewability feeds entirely; they are S3-only
and not deliverable via Snowflake.

#### 3.2.5 REDS Conversions

`LogEntryTime`, `ConversionId`, `AdvertiserId`, `ConversionType` (tracking-tag ID),
`IPAddress`, `ReferrerUrl`, `MonetaryValue`, `MonetaryValueCurrency`, `OrderId`,
`TD1`–`TD10`, `ProcessedTime`, `UserAgent`, `CombinedIdentifier`,
`CombinedIdentifierType`, `OfflineConversionTime`, `OfflineProviderID`.

Two generation rules with intent behind them:

- **Populate `MonetaryValue`, `OrderId` and `TD1`–`TD10` sparsely.** They are empty
  in TTD's own sample because they depend on advertiser pixel implementation. That
  gap *is* the Affinity value proposition — TTD sees the pixel fire but often not
  the basket. Make it visible rather than tidy.
- **Populate `OfflineProviderID` on a thin slice**, to show the integration socket
  Affinity would occupy.

**Conversions do not join to Impressions on impression ID.** Join on
`CombinedIdentifier` **and** `CombinedIdentifierType` together, always carrying
`LogEntryTime`.

---

### Demo output tables (§5A.1)

#### Output schema (`TTD_CONSUMER.DEMO_OUTPUT`)

| Table | Description |
|---|---|
| `BIDDING_RULES` | 500-700 rules: `RULE_ID`, `PREDICATE` (in TTD REDS field names), `BID_MULTIPLIER`, `SUPPORT`, `LIFT`, `CONFIDENCE_INTERVAL`, `MATCH_TIER`, `VALID_FROM/TO` |
| `PREDICTION_MULTIPLIERS` | Per matched individual × brand: `CLIENT_ID`, `BRAND_ID`, `BID_MULTIPLIER`, `PERCENTILE_RANK`, `PREDICTED_SPEND_30D` |
| `CONVERSION_ENRICHMENT` | Affinity purchases attributed to REDS impressions: `ImpressionId`, `TXID`, `BRAND_NAME`, `TRANS_AMOUNT`, `MATCH_CODE` |
| `ACCURACY_PROOF` | Q3 prediction vs Q4 actuals: `INDID`, `BRAND_ID`, `PREDICTED_SPEND`, `ACTUAL_SPEND`, `PERCENTILE_RANK` |
