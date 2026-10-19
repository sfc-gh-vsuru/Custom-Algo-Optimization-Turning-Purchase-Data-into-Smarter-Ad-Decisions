# PubMatic — Data Model (SSP Consumer)

PubMatic consumer-side data: a flattened OpenRTB 2.6 bid-request impression log and its identity mapping. Followed by the demo output tables built on top.

> Extracted from `DEMO_BUILD_PLAN.md`. Section numbers (§) refer to that document. All data in the demo is synthetic, generated to these specifications.

---

### 3.3 PubMatic consumer data (SSP) — OpenRTB flattened impression log

PubMatic is an SSP. It sees bid requests (OpenRTB 2.6), not post-impression
outcomes. The consumer dataset is a **flattened impression log** derived from
OpenRTB bid-request objects, representing what PubMatic would share into a DCR.

**No conversion feed exists on the SSP side.** Affinity purchase outcomes are the
*entire* label — this is the core value proposition for SSPs.

#### 3.3.1 PubMatic impression log

| Column | OpenRTB source | Type | Description |
|---|---|---|---|
| `AUCTION_ID` | `BidRequest.id` | VARCHAR | Unique bid request ID |
| `TIMESTAMP` | generated | TIMESTAMP | Auction timestamp |
| `SITE_DOMAIN` | `site.domain` | VARCHAR | Publisher domain |
| `SITE_PAGE` | `site.page` | VARCHAR | Page URL |
| `SITE_CAT` | `site.cat` | VARCHAR | IAB content category |
| `PUBLISHER_ID` | `publisher.id` | VARCHAR | Exchange-specific publisher ID |
| `PUBLISHER_NAME` | `publisher.name` | VARCHAR | Publisher name |
| `IMP_ID` | `imp.id` | VARCHAR | Impression ID within request |
| `AD_FORMAT` | `imp.banner`/`video`/`native` presence | VARCHAR | `banner`, `video`, `audio`, `native` |
| `BANNER_W` | `banner.w` | INTEGER | Banner width (DIPS) |
| `BANNER_H` | `banner.h` | INTEGER | Banner height (DIPS) |
| `BANNER_POS` | `banner.pos` | INTEGER | Ad position on screen |
| `VIDEO_PLACEMENT` | `video.placement` | INTEGER | In-stream, out-stream, etc. |
| `VIDEO_STARTDELAY` | `video.startdelay` | INTEGER | Pre/mid/post-roll |
| `BIDFLOOR` | `imp.bidfloor` | FLOAT | Minimum bid CPM |
| `BIDFLOORCUR` | `imp.bidfloorcur` | VARCHAR | Floor currency |
| `DEAL_ID` | `deal.id` | VARCHAR | PMP deal ID (nullable) |
| `DEVICE_TYPE` | `device.devicetype` | INTEGER | AdCOM device type enum |
| `DEVICE_MAKE` | `device.make` | VARCHAR | e.g. "Apple" |
| `DEVICE_MODEL` | `device.model` | VARCHAR | e.g. "iPhone" |
| `DEVICE_OS` | `device.os` | VARCHAR | e.g. "iOS" |
| `DEVICE_UA` | `device.ua` | VARCHAR | User agent string |
| `DEVICE_CARRIER` | `device.carrier` | VARCHAR | Carrier/ISP |
| `DEVICE_IP` | `device.ip` | VARCHAR | IPv4 address |
| `GEO_ZIP` | `geo.zip` | VARCHAR | 5-digit zip |
| `GEO_CITY` | `geo.city` | VARCHAR | City |
| `GEO_REGION` | `geo.region` | VARCHAR | State/region |
| `GEO_METRO` | `geo.metro` | VARCHAR | Nielsen DMA |
| `GEO_LAT` | `geo.lat` | FLOAT | Latitude (2dp) |
| `GEO_LON` | `geo.lon` | FLOAT | Longitude (2dp) |
| `GEO_COUNTRY` | `geo.country` | VARCHAR | ISO-3166-1 alpha-3 |
| `USER_EID_SOURCE` | `user.eids[].source` | VARCHAR | Identity provider (e.g. `uidapi.com`, `liveramp.com`) |
| `USER_EID_UID` | `user.eids[].uids[].id` | VARCHAR | User ID from that provider |
| `USER_EID_ATYPE` | `user.eids[].uids[].atype` | INTEGER | Agent type |
| `DEVICE_IFA` | `device.ifa` | VARCHAR | IDFA/GAID (nullable) |
| `CONTENT_TITLE` | `content.title` | VARCHAR | Content title |
| `CONTENT_GENRE` | `content.genre` | VARCHAR | Content genre |
| `CONTENT_NETWORK` | `content.network.name` | VARCHAR | CTV network |
| `CONTENT_CHANNEL` | `content.channel.name` | VARCHAR | CTV channel |
| `CONTENT_LIVESTREAM` | `content.livestream` | INTEGER | 0/1 live |
| `CONTENT_LEN` | `content.len` | INTEGER | Content duration (seconds) |
| `AUCTION_TYPE` | `BidRequest.at` | INTEGER | 1=first price, 2=second price |
| `SECURE` | `imp.secure` | INTEGER | HTTPS required |
| `WINNING_PRICE` | generated | FLOAT | Clearing price (post-auction, for log) |

#### 3.3.2 Identity mapping for PubMatic

| Affinity method | PubMatic field | Coverage notes |
|---|---|---|
| `MDI1` / `MDH1` (MAID) | `DEVICE_IFA` | In-app only; null for web |
| `IPA1` (IP) | `DEVICE_IP` | Always present |
| `HEM1` (hashed email) | `USER_EID_UID` where source = `uidapi.com` | UID2-based; logged-in web |
| RampID | `USER_EID_UID` where source = `liveramp.com` | Where available |

**Note:** PubMatic has no name/address fields — `EXCT`, `FZY*`, `HHD1`, `HHD2`
methods will not fire. Match rates will be lower, driven by MAID, UID2/RampID,
and IP. This is realistic and worth showing — it demonstrates why SSP-side
matching is harder and why Affinity's broad identity coverage matters.

---

### Demo output tables (§5A.2)

#### Output schema (`PUBMATIC_CONSUMER.DEMO_OUTPUT`)

| Table | Description |
|---|---|
| `INVENTORY_YIELD_SCORES` | Per supply dimension combo: `SITE_DOMAIN`, `AD_FORMAT`, `DEVICE_TYPE`, `GEO_DMA`, `CONTENT_GENRE`, `PURCHASE_RATE`, `BASELINE_RATE`, `YIELD_MULTIPLIER`, `SUPPORT` |
| `FLOOR_RECOMMENDATIONS` | Recommended floor prices by inventory segment: `SEGMENT_ID`, `DIMENSIONS`, `CURRENT_AVG_FLOOR`, `RECOMMENDED_FLOOR`, `EXPECTED_REVENUE_LIFT` |
| `PURCHASE_INVENTORY_PACKAGES` | Pre-built inventory packages for advertisers: `PACKAGE_NAME`, `INCLUDED_DOMAINS`, `INCLUDED_FORMATS`, `PURCHASE_RATE`, `ESTIMATED_REACH` |
| `MATCH_SUMMARY` | Match rates by identity method |
