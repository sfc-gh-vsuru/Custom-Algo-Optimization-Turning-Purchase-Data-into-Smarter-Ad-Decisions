# ML Setup Guide — Training the Models (PubMatic Example)

This guide shows how to build the **Snowflake ML** part of the demo from scratch, using **PubMatic** as the worked example. It picks up after the data setup is complete.

---

## Why this step exists

The main setup (`setup/01` → `02` → `03`) loads **model results** from CSV files: decile lift, feature importance, holdout checks and model-registry rows. That is enough for every dashboard to work.

It does **not** create the models themselves, so after the main setup you cannot retrain them or score new data. This ML setup adds that.

| | After main setup (01–03) | After ML setup (04) |
|---|---|---|
| Dashboards work | Yes | Yes |
| Model results (deciles, importance, holdout) | Loaded from CSV | Recomputed from the trained models |
| Model objects (`SNOWFLAKE.ML.CLASSIFICATION`) | No | Yes |
| Training data | No | Yes (~2.5M labeled rows) |
| Can call `!PREDICT` on new data | No | Yes |

---

## Prerequisites

1. `setup/01_environment.sql`, `setup/02_load_data.sql` and `setup/03_streamlit_apps.sql` have been run.
2. Warehouse `AFFINITY_GEN_WH` exists (created in 01). A **LARGE** warehouse is recommended for training.
3. The role has `CREATE SNOWFLAKE.ML.CLASSIFICATION` privilege on schema `AFFINITY_DEMO.ML`, plus create-table rights on `ML` and `PUBMATIC_CONSUMER`.

---

## How to run

**Option A: Snowsight.** Open `setup/04_ml_pubmatic.sql` in a SQL worksheet and choose **Run All**.

**Option B: Snowflake CLI.**

```bash
snow sql -f setup/04_ml_pubmatic.sql --connection <your_connection> --enable-templating NONE
```

> `--enable-templating NONE` is required. The data contains the text `AT&T`, which the CLI otherwise reads as a template variable and stops with *"'T' is undefined"*.

**Runtime:** about 15–30 minutes on a LARGE warehouse. Training (Step 4) takes the longest.

**Safe to re-run:** every random draw is hash-based, so each run produces the same data and labels.

---

## What the script does

```
OPENRTB_IMPRESSIONS (10M)  ──►  MATCHING_INPUT
         │
         ▼
TRAINING_SET_PUBMATIC (~2.5M, 80% train / 20% holdout)
         │
         ├──► PUBMATIC_YIELD_CLASSIFIER  (will it lead to a purchase?)
         └──► PUBMATIC_SPEND_CLASSIFIER  (how much will they spend?)
                    │
                    ▼
   Holdout scoring ─► Deciles ─► Feature importance ─► Holdout check ─► Registry
                    │
                    ▼
   (optional) Refresh dashboard tables: rules, tiers, yield, floors, packages
```

| Step | What happens | Output |
|---|---|---|
| **1. Impression log** | Generates 10M flattened OpenRTB bid requests (site, format, device, geo, floor price, IDs, CTV content) in two 5M batches | `PUBMATIC_CONSUMER.OPENRTB_IMPRESSIONS` |
| **2. Matching input** | Pulls the IDs PubMatic would send to the clean room: device ID, UID2 / RampID, IP | `PUBMATIC_CONSUMER.MATCHING_INPUT` |
| **3. Training set** | Takes a 25% sample, gives each impression a purchase probability from supply-side factors (device, format, genre, site, metro), draws the purchase outcome, spend and transactions, and sets aside 20% as holdout | `ML.TRAINING_SET_PUBMATIC` |
| **4. Train** | Trains two Snowflake ML classifiers on training rows only (`IS_HOLDOUT = 0`) | `ML.PUBMATIC_YIELD_CLASSIFIER`, `ML.PUBMATIC_SPEND_CLASSIFIER` |
| **5. Evaluate** | Scores the unseen holdout and builds decile lift, feature importance, training-vs-holdout comparison, and built-in metrics (AUC etc.) | `ML.PUBMATIC_YIELD_PREDICTIONS`, `ML.PUBMATIC_VALIDATION_DECILES`, `ML.PUBMATIC_FEATURE_IMPORTANCE`, `ML.PUBMATIC_HOLDOUT_RESULTS` |
| **6. Register** | Refreshes the two PubMatic rows in the registry, with key metrics filled in from the new results | `ML.MODEL_REGISTRY` |
| **7. Dashboard refresh** *(optional)* | Rebuilds PubMatic's dashboard tables from the new training data | `PUBMATIC_CONSUMER.DEMO_OUTPUT_*` (SSP rules, publisher multipliers, yield scores, floors, packages) |

> **Step 7 is optional.** It replaces the dashboard tables loaded from CSV with ones built from the new training data. Delete or comment out that section to keep the dashboard exactly as shipped.

### Model inputs

| Model | Predicts | Features |
|---|---|---|
| `PUBMATIC_YIELD_CLASSIFIER` | `PURCHASED` (0/1) | `SITE_DOMAIN`, `AD_FORMAT`, `PUBLISHER_NAME`, `DEVICE_TYPE`, `GEO_METRO`, `BIDFLOOR`, `CONTENT_GENRE`, `BANNER_POS`, `AUCTION_TYPE`, `COMPOSITE_PROPENSITY` |
| `PUBMATIC_SPEND_CLASSIFIER` | `SPEND_TIER` (HIGH / MID / LOW / NO_PURCHASE) | `SITE_DOMAIN`, `AD_FORMAT`, `PUBLISHER_NAME`, `DEVICE_TYPE`, `GEO_METRO`, `BIDFLOOR`, `CONTENT_GENRE`, `COMPOSITE_PROPENSITY` |

---

## What to expect

| Check | Expected (full run) |
|---|---|
| `OPENRTB_IMPRESSIONS` rows | 10,000,000 |
| `TRAINING_SET_PUBMATIC` rows | ~2.5M |
| Purchase rate | ~1.07% |
| Holdout share | 20% |
| Top decile lift | ~2.5x |
| Top 3 deciles capture | ~55% of purchases |
| #1 feature | `BIDFLOOR`, then `COMPOSITE_PROPENSITY` |
| SSP rules (if Step 7 runs) | ~270 |

The script ends with a verification query that prints these.

**Reading the evaluation metrics (Step 5e):**
- Use **AUC** and **decile lift** to judge the model.
- Training and holdout purchase rates should be about the same. That means no overfitting; it is not a lift claim.
- Expect **"precision / F1 not defined"** notes for the purchase class. With purchases around 1%, the model rarely predicts "purchase" at the default 50% cutoff. That's normal for rare events and is why the demo ranks by score (deciles) instead.

---

## Using the trained models

Score any impression:

```sql
SELECT AFFINITY_DEMO.ML.PUBMATIC_YIELD_CLASSIFIER!PREDICT(INPUT_DATA => OBJECT_CONSTRUCT(
  'SITE_DOMAIN','espn.com', 'AD_FORMAT','video', 'PUBLISHER_NAME','ESPN Digital',
  'DEVICE_TYPE',3, 'GEO_METRO','Los Angeles', 'BIDFLOOR',8.5,
  'CONTENT_GENRE','Sports', 'BANNER_POS',1, 'AUCTION_TYPE',1,
  'COMPOSITE_PROPENSITY',0.05)):probability:"1"::FLOAT AS PURCHASE_PROBABILITY;
```

Inspect a model:

```sql
CALL AFFINITY_DEMO.ML.PUBMATIC_YIELD_CLASSIFIER!SHOW_FEATURE_IMPORTANCE();
CALL AFFINITY_DEMO.ML.PUBMATIC_YIELD_CLASSIFIER!SHOW_GLOBAL_EVALUATION_METRICS();
CALL AFFINITY_DEMO.ML.PUBMATIC_YIELD_CLASSIFIER!SHOW_CONFUSION_MATRIX();
```

---

## Applying the same pattern to other platforms

Every platform in the demo follows the same five-step ML recipe. To adapt the script, swap the source table and the features:

1. **Source log:** the platform's impression or event table.
2. **Training set:** add a purchase probability (base rate × factor multipliers), a hash-based purchase draw, spend, and `IS_HOLDOUT` (20%).
3. **Train:** `CREATE SNOWFLAKE.ML.CLASSIFICATION` on `IS_HOLDOUT = 0`, once for purchase and once for spend tier.
4. **Evaluate:** `!PREDICT` on the holdout, then deciles (`NTILE(10)`), feature importance, and the training-vs-holdout comparison.
5. **Register:** add the model rows to `ML.MODEL_REGISTRY`.

---

## Best practices built into the script

| Practice | Why |
|---|---|
| Hash-based draws, never `RANDOM()` | Re-runs produce the same data; `RANDOM()` is re-evaluated each time it's referenced |
| Index-only generator, then 5M-row batches | Large generators with joins time out |
| Sampling with `ABS(HASH(id,123)) % 100 < N` | `SAMPLE (N ROWS)` returns a fixed row count, not a percentage |
| Training input is a permanent table | A temporary input table failed for the forecast model earlier in this build; permanent is the safe default |
| Feature importance via `CALL` + `RESULT_SCAN` | `TABLE(model!SHOW_FEATURE_IMPORTANCE())` fails |
| Holdout labelled "Training" vs "Holdout" | Avoids implying the rules caused the (nearly identical) rates |
| Rules use only fields known when the ad is sold | So the rules can actually be applied live |
| Small samples shrunk toward 1.0 | A few lucky impressions can't produce extreme multipliers |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| CLI: `'T' is undefined` | Add `--enable-templating NONE` |
| Insufficient privileges on `CREATE ... CLASSIFICATION` | Grant `CREATE SNOWFLAKE.ML.CLASSIFICATION ON SCHEMA AFFINITY_DEMO.ML` to your role |
| Training times out | Use a LARGE (or bigger) warehouse; in Snowsight, raise the statement timeout |
| Dashboard numbers changed | Step 7 rebuilt the dashboard tables. Re-run `02_load_data.sql` to restore the shipped CSV results |
