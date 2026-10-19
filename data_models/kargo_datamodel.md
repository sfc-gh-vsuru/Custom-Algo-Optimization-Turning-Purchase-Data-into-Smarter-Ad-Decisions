# Kargo — Data Model (Ad Server / Publisher Consumer)

Kargo consumer-side data: the Log Level Data (LLD) event table and its identity mapping. Followed by the demo output tables built on top.

> Extracted from `DEMO_BUILD_PLAN.md`. Section numbers (§) refer to that document. All data in the demo is synthetic, generated to these specifications.

---

### 3.4 Kargo consumer data (ad server / publisher) — LLD event log

Kargo delivers Log Level Data (LLD) as daily gzipped CSVs. Schema from
`Log Level Data Process Request Form and FAQ_KARGO.xlsx`, LLD Schema V0 tab.

#### 3.4.1 Kargo LLD event table

| Column | Type | Description |
|---|---|---|
| `AUCTION_ID` | VARCHAR | Kargo auction tracking ID |
| `AUCTION_TYPE` | VARCHAR | `Direct`, `Preferred`, `Private`, `PG`, `PMP`, `Unknown` |
| `EVENT_TIMESTAMP` | TIMESTAMP | `YYYY-MM-DD HH:MM:SS` |
| `EVENT_TYPE` | VARCHAR | `impression`, `click`, `video_load`, `video_start`, `video_skip`, `video_firstquartile`, `video_midpoint`, `video_thirdquartile`, `video_complete` |
| `MOAT_INVIEW_MEASURABLE` | INTEGER | 0/1 — viewability measured by MOAT |
| `MOAT_INVIEW_VIEWABLE` | INTEGER | 0/1 — viewable per IAB standard |
| `ADVERTISER_ID` | VARCHAR | Kargo advertiser ID |
| `ADVERTISER_NAME` | VARCHAR | Advertiser name |
| `DEMAND_TYPE` | VARCHAR | `campaign` or `deal_group` |
| `CAMPAIGN_DEAL_GROUP_ID` | INTEGER | Campaign (Direct) / deal group (PMP) ID |
| `CAMPAIGN_DEAL_GROUP_NAME` | VARCHAR | Campaign / deal group name |
| `PLACEMENT_ID` | INTEGER | Kargo placement ID |
| `PLACEMENT_NAME` | VARCHAR | Placement name |
| `PLACEMENT_TYPE` | VARCHAR | `standard`, `added_value`, `branded_takeover`, `social_canvas` |
| `LINE_ITEM_DEAL_ID` | VARCHAR | Line item / deal ID |
| `LINE_ITEM_DEAL_NAME` | VARCHAR | Line item / deal name |
| `PUBLISHER_ID` | INTEGER | Kargo publisher ID |
| `PUBLISHER_NAME` | VARCHAR | Publisher name |
| `PUBLISHER_DOMAIN` | VARCHAR | Publisher domain |
| `AD_SLOT_NAME` | VARCHAR | Ad slot name + platform (e.g. "Hover (Mobile Web)") |
| `MEDIA_TYPE` | VARCHAR | `banner`, `video`, `native` |
| `CREATIVE_ID` | VARCHAR | Kargo creative ID |
| `CREATIVE_NAME` | VARCHAR | Creative name |
| `CREATIVE_SIZE` | VARCHAR | e.g. `300x250`, `320x50` |
| `CREATIVE_FORMAT` | VARCHAR | e.g. `ABA Display`, `Runway`, `Breakaway` |
| `KARGO_RAMP_ID` | VARCHAR | LiveRamp Kargo-specific RampID; `kg-` prefix = no mapping; null = no cookie/IFA |
| `IFA` | VARCHAR | Device IDFA/GAID; null for non-video/display |
| `DEVICE_TYPE` | VARCHAR | `Computer`, `Mobile`, `Tablet`, etc. |
| `DEVICE_PLATFORM` | VARCHAR | CTV platform (e.g. `Roku`, `LG Smart TV`, `XUMO`) |
| `APP_STORE_URL` | VARCHAR | App store URL (CTV) |
| `APP_STORE_ID` | VARCHAR | App store ID (CTV) |
| `APP_NAME` | VARCHAR | App name (CTV) |
| `APP_BUNDLE_ID` | VARCHAR | App bundle ID (CTV) |
| `OS` | VARCHAR | Operating system |
| `SOCIAL_BROWSER` | VARCHAR | Social media platform if in-app browser |
| `BROWSER` | VARCHAR | Browser type |
| `LANGUAGE` | VARCHAR | Content language |
| `IP_ADDRESS` | VARCHAR | Device IP address |
| `DMA` | VARCHAR | Nielsen DMA |
| `CITY` | VARCHAR | City (IP-derived) |
| `STATE_REGION` | VARCHAR | State/province (IP-derived) |
| `COUNTRY_CODE` | VARCHAR | 2-letter country code |
| `POSTAL_CODE` | VARCHAR | Postal code (IP-derived) |
| `CARRIER` | VARCHAR | Phone carrier |
| `COMPANY` | VARCHAR | Internet carrier company |
| `HOME_BIZ` | VARCHAR | `home` or `business` (IP-derived) |
| `CONNECTION_TYPE` | VARCHAR | `wifi`, `mobile`, `wired`, `cable`, `xdsl`, `broadband` |

#### 3.4.2 Identity mapping for Kargo

| Affinity method | Kargo field | Coverage notes |
|---|---|---|
| RampID | `KARGO_RAMP_ID` | Primary; `kg-` prefix rows have no LiveRamp mapping |
| `MDI1` / `MDH1` (MAID) | `IFA` | Video/CTV only; null for display |
| `IPA1` (IP) | `IP_ADDRESS` | Always present |

**No name, email, or address fields.** Only MAID, RampID, and IP
methods fire. CTV inventory will lean heavily on `IPA1` due to limited IFA
availability on CTV devices.

#### 3.4.3 What makes Kargo data distinctive

- **Event-level granularity** — not just impressions but clicks and video quartile
  events. This enables engagement-weighted labels (e.g., a video completion +
  purchase is stronger signal than an impression + purchase).
- **Viewability built in** — `MOAT_INVIEW_MEASURABLE` / `MOAT_INVIEW_VIEWABLE`
  allow viewability-conditioned analysis without a separate feed.
- **CTV-specific fields** — `DEVICE_PLATFORM`, `APP_NAME`, `APP_BUNDLE_ID` enable
  CTV-specific rule derivation, which is the highest-value inventory segment.
- **No economics fields** — Kargo LLD has no cost data. Rules optimize on
  purchase conversion rate and engagement quality, not spend efficiency.

---

### Demo output tables (§5A.3)

#### Output schema (`KARGO_CONSUMER.DEMO_OUTPUT`)

| Table | Description |
|---|---|
| `ENGAGEMENT_PURCHASE_ATTRIBUTION` | Per event × matched purchase: `AUCTION_ID`, `EVENT_TYPE`, `PUBLISHER_DOMAIN`, `CREATIVE_FORMAT`, `TXID`, `BRAND_NAME`, `TRANS_AMOUNT`, `MATCH_CODE` |
| `PLACEMENT_PURCHASE_SCORES` | Per placement: `PLACEMENT_NAME`, `PLACEMENT_TYPE`, `CREATIVE_FORMAT`, `IMPRESSIONS`, `VIEWABLE_IMPRESSIONS`, `VIDEO_COMPLETIONS`, `PURCHASES`, `PURCHASE_RATE`, `VIEWABLE_PURCHASE_RATE` |
| `CTV_ATTRIBUTION` | CTV-specific: `DEVICE_PLATFORM`, `APP_NAME`, `APP_BUNDLE_ID`, `IMPRESSIONS`, `VIDEO_COMPLETIONS`, `PURCHASES`, `PURCHASE_RATE` |
| `ENGAGEMENT_QUALITY_RULES` | Rules in Kargo field names: `RULE_ID`, `PREDICATE`, `PURCHASE_RATE`, `LIFT`, `SUPPORT`, targeting creative format, placement type, publisher, DMA, device platform |
