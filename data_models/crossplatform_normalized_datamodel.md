# Cross-Platform — Normalized Data Model

The shared mapping that puts every vendor's fields into one common feature space for machine learning.

> Extracted from `DEMO_BUILD_PLAN.md`. Section numbers (§) refer to that document. All data in the demo is synthetic, generated to these specifications.

---

### 3.6 Normalized impression model

A platform-agnostic view that maps each platform's fields to a common feature
space for ML training. Lives in `NORMALIZED` schema.

| Normalized field | TTD source | PubMatic source | Kargo source | AdRoll source |
|---|---|---|---|---|
| `PLATFORM` | `'TTD'` | `'PUBMATIC'` | `'KARGO'` | `'ADROLL'` |
| `IMPRESSION_ID` | `ImpressionId` | `AUCTION_ID\|\|IMP_ID` | `AUCTION_ID` | `CONVERSION_ID` |
| `TIMESTAMP` | `LogEntryTime` | `TIMESTAMP` | `EVENT_TIMESTAMP` | `CONVERSION_TIMESTAMP` |
| `DEVICE_TYPE` | `DeviceType` (enum) | `DEVICE_TYPE` (enum) | `DEVICE_TYPE` (string) | `DEVICE_TYPE` (string) |
| `OS` | `OS` (enum) | `DEVICE_OS` | `OS` | `OS` |
| `BROWSER` | `Browser` (enum) | derived from `DEVICE_UA` | `BROWSER` | `BROWSER` |
| `GEO_ZIP` | `Zip` | `GEO_ZIP` | `POSTAL_CODE` | NULL |
| `GEO_DMA` | `NielsenDMA` | `GEO_METRO` | `DMA` | `GEO_DMA` |
| `GEO_STATE` | `Region` | `GEO_REGION` | `STATE_REGION` | `GEO_REGION` |
| `IP_ADDRESS` | `IPAddress` | `DEVICE_IP` | `IP_ADDRESS` | `IP_ADDRESS` |
| `SUPPLY_DOMAIN` | `Site` | `SITE_DOMAIN` | `PUBLISHER_DOMAIN` | `LANDING_PAGE_URL` (domain) |
| `AD_FORMAT` | `AdFormat` (enum) | `AD_FORMAT` | `MEDIA_TYPE` | `CHANNEL` |
| `CREATIVE_SIZE` | derived from format enums | `BANNER_W\|\|x\|\|BANNER_H` | `CREATIVE_SIZE` | NULL |
| `CONTENT_GENRE` | `ContentGenre1` | `CONTENT_GENRE` | NULL | NULL |
| `CONTENT_NETWORK` | `ContentNetwork` | `CONTENT_NETWORK` | NULL | NULL |
| `CTV_APP` | NULL | NULL | `APP_NAME` | NULL |
| `CTV_PLATFORM` | NULL | NULL | `DEVICE_PLATFORM` | NULL |
| `CARRIER` | `Carrier` | `DEVICE_CARRIER` | `CARRIER` | NULL |
| `VIEWABLE` | NULL (separate feed) | NULL | `MOAT_INVIEW_VIEWABLE` | NULL |
| `VIDEO_COMPLETION` | NULL (VideoEvents feed) | NULL | derived from `EVENT_TYPE` | `VIDEO_COMPLETION_RATE` |
| `USER_HOUR_OF_WEEK` | `UserHourOfWeek` (0-167) | derived from timestamp | derived from timestamp | derived from timestamp |
| `ATTRIBUTED_REVENUE` | NULL | NULL | NULL | `ATTRIBUTED_REVENUE` |
| `CHANNEL` | NULL | NULL | NULL | `CHANNEL` |
| `ATTRIBUTION_TYPE` | NULL | NULL | NULL | `ATTRIBUTION_TYPE` |

**Note:** AdRoll's normalized rows represent conversions, not impressions. The
`IMPRESSION_ID` maps to `CONVERSION_ID`. AdRoll-specific fields (`ATTRIBUTED_REVENUE`,
`CHANNEL`, `ATTRIBUTION_TYPE`) are NULL for other platforms and vice versa.

UDFs in `UTIL` handle enum translation (e.g., TTD `DeviceType` integer → string,
PubMatic AdCOM `devicetype` integer → string, Kargo string passthrough).
