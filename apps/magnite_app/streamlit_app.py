import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import altair as alt

session = get_active_session()

st.set_page_config(page_title="Magnite Outcome Intelligence", layout="wide", page_icon="📺")
st.title("📺 Magnite CTV + Deal Outcome Intelligence")
st.caption("Affinity Solutions × Magnite — Purchase-verified CTV yield, deals, and buyer outcomes with Snowflake ML")

DB = "AFFINITY_DEMO.MAGNITE_CONSUMER"
ACTION_COLORS = alt.Scale(domain=['BOOST', 'NEUTRAL', 'SUPPRESS'], range=['#2ecc71', '#95a5a6', '#e74c3c'])


@st.cache_data(ttl=3600)
def q(sql):
    return session.sql(sql).to_pandas()


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Identity Coverage", "CTV Yield", "Verified Deals + Packages",
    "Buyer Outcomes", "Pricing Rules", "Cross-Screen", "ML Models"
])

# ── Tab 1: Identity Coverage ────────────────────────────────────────────────
with tab1:
    st.header("Identity Coverage — Streaming + DV+ Log-Level Data")
    st.caption("Magnite exposure logs are matched to Affinity's purchase panel inside the clean room. No raw IDs are shared either way.")

    match = q("SELECT * FROM AFFINITY_DEMO.CLEANROOM.MAGNITE_MATCH_RATE_SUMMARY ORDER BY WATERFALL_STEP")
    cov = q(f"SELECT * FROM {DB}.DEMO_OUTPUT_IDENTITY_COVERAGE ORDER BY FEED DESC, MATCHED_IMPRESSIONS DESC")

    total_imps = int(cov['IMPRESSIONS'].sum())
    matched_imps = int(cov['MATCHED_IMPRESSIONS'].sum())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Affinity Match Rate", f"{match['PCT_OF_TOTAL_AFS'].sum():.1f}%", delta=f"{int(match['MATCHED_COUNT'].sum()):,} individuals")
    c2.metric("Impressions Analyzed", f"{total_imps/1e6:.1f}M", delta="Streaming + DV+")
    c3.metric("Impressions with Purchase Data", f"{matched_imps/1e6:.2f}M", delta=f"{matched_imps/total_imps*100:.1f}% of all")
    c4.metric("Households (IP match)", f"{int(match['HH_ONLY_COUNT'].sum()):,}")

    c1, c2 = st.columns(2)
    with c1:
        bar = alt.Chart(match).mark_bar().encode(
            x=alt.X('MATCH_CODE:N', sort=alt.EncodingSortField(field='WATERFALL_STEP'), title='Match method'),
            y=alt.Y('MATCHED_COUNT:Q', title='Matched individuals'),
            color=alt.Color('MATCH_LEVEL:N', scale=alt.Scale(domain=['INDIVIDUAL', 'HOUSEHOLD'], range=['#3498db', '#e67e22'])),
            tooltip=['MATCH_CODE', 'MATCH_LEVEL', 'MATCHED_COUNT', 'PCT_OF_TOTAL_AFS']
        ).properties(height=320, title='Matches by method (waterfall order)')
        st.altair_chart(bar, use_container_width=True)
        st.caption("HEM1 = UID2 / Yahoo ConnectID (email-based). MDI1 = device ID. IPA1 = IP address, matched to a household.")
    with c2:
        cov_long = cov.assign(UNMATCHED=cov['IMPRESSIONS'] - cov['MATCHED_IMPRESSIONS'])
        cov_long['FEED_ID'] = cov_long['FEED'] + ' · ' + cov_long['ID_TYPE']
        cov_long = cov_long.melt(id_vars=['FEED_ID'], value_vars=['MATCHED_IMPRESSIONS', 'UNMATCHED'], var_name='STATUS', value_name='IMPS')
        stack = alt.Chart(cov_long).mark_bar().encode(
            x=alt.X('IMPS:Q', title='Impressions'),
            y=alt.Y('FEED_ID:N', title='', sort='-x'),
            color=alt.Color('STATUS:N', scale=alt.Scale(domain=['MATCHED_IMPRESSIONS', 'UNMATCHED'], range=['#2ecc71', '#dfe6e9']), title=''),
            tooltip=['FEED_ID', 'STATUS', 'IMPS']
        ).properties(height=320, title='Impressions matched by feed and ID type')
        st.altair_chart(stack, use_container_width=True)
        st.caption("Green = impressions Affinity can tie to purchases. RampID and no-ID traffic stay unmatched in this demo.")

    st.dataframe(cov, use_container_width=True)

# ── Tab 2: CTV Yield ────────────────────────────────────────────────────────
with tab2:
    st.header("CTV Purchase Yield — Which Streaming Supply Drives Sales")
    st.caption("Yield index = purchase rate ÷ average. 1.0 = average, 2.0 = twice as likely to lead to a purchase.")

    ctv = q(f"""SELECT SUPPLY_NAME, GENRE, DEVICE_CLASS, SUM(MATCHED_IMPRESSIONS) IMPS, SUM(PURCHASES) PURCHASES,
        ROUND(SUM(PURCHASES)/SUM(MATCHED_IMPRESSIONS)*100,3) PURCHASE_RATE_PCT,
        ROUND(SUM(PURCHASES)/SUM(MATCHED_IMPRESSIONS) / (SELECT AVG(PURCHASED) FROM AFFINITY_DEMO.ML.TRAINING_SET_MAGNITE),2) YIELD_INDEX
        FROM {DB}.DEMO_OUTPUT_SUPPLY_YIELD WHERE FEED='STREAMING' GROUP BY 1,2,3""")
    feed = q(f"""SELECT FEED, ROUND(SUM(PURCHASES)/SUM(MATCHED_IMPRESSIONS)*100,3) PURCHASE_RATE_PCT,
        ROUND(SUM(PURCHASE_VALUE)/SUM(MATCHED_IMPRESSIONS)*1000,2) VALUE_PER_1K FROM {DB}.DEMO_OUTPUT_SUPPLY_YIELD GROUP BY 1""").set_index('FEED')

    c1, c2, c3 = st.columns(3)
    c1.metric("CTV / Streaming Purchase Rate", f"{feed.loc['STREAMING','PURCHASE_RATE_PCT']}%")
    c2.metric("Display / Video (DV+) Purchase Rate", f"{feed.loc['DVPLUS','PURCHASE_RATE_PCT']}%")
    c3.metric("Streaming vs DV+", f"{feed.loc['STREAMING','PURCHASE_RATE_PCT']/feed.loc['DVPLUS','PURCHASE_RATE_PCT']:.1f}x",
              delta=f"${feed.loc['STREAMING','VALUE_PER_1K']:,.0f} sales per 1K CTV imps")

    heat = alt.Chart(ctv[ctv['IMPS'] >= 500]).mark_rect().encode(
        x=alt.X('DEVICE_CLASS:N', title='Platform family'),
        y=alt.Y('SUPPLY_NAME:N', sort='-color', title='Streaming app'),
        color=alt.Color('YIELD_INDEX:Q', scale=alt.Scale(scheme='redyellowgreen'), title='Yield index'),
        tooltip=['SUPPLY_NAME', 'GENRE', 'DEVICE_CLASS', 'YIELD_INDEX', 'PURCHASE_RATE_PCT', 'IMPS', 'PURCHASES']
    ).properties(height=440, title='Purchase yield: streaming app × platform family')
    st.altair_chart(heat, use_container_width=True)
    st.caption("Green = sells well. Home, cooking and sports apps on the big screen lead; kids and classic TV trail.")

    c1, c2 = st.columns(2)
    with c1:
        dp = q(f"""SELECT DAYPART, ROUND(SUM(PURCHASES)/SUM(MATCHED_IMPRESSIONS)*100,3) PURCHASE_RATE_PCT
            FROM {DB}.DEMO_OUTPUT_SUPPLY_YIELD WHERE FEED='STREAMING' GROUP BY 1""")
        st.altair_chart(alt.Chart(dp).mark_bar(color='#8e44ad').encode(
            x=alt.X('DAYPART:N', sort=['Morning', 'Afternoon', 'Evening', 'LateNight'], title='Daypart'),
            y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase rate %'), tooltip=['DAYPART', 'PURCHASE_RATE_PCT']
        ).properties(height=280, title='CTV purchase rate by daypart'), use_container_width=True)
        st.caption("Evening prime time converts best — worth a premium price.")
    with c2:
        ps = q(f"""SELECT AD_SIZE PLAYER_SIZE, ROUND(SUM(PURCHASES)/SUM(MATCHED_IMPRESSIONS)*100,3) PURCHASE_RATE_PCT
            FROM {DB}.DEMO_OUTPUT_SUPPLY_YIELD WHERE FEED='STREAMING' GROUP BY 1""")
        st.altair_chart(alt.Chart(ps).mark_bar(color='#16a085').encode(
            x=alt.X('PLAYER_SIZE:N', sort='-y', title='Player size'),
            y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase rate %'), tooltip=['PLAYER_SIZE', 'PURCHASE_RATE_PCT']
        ).properties(height=280, title='CTV purchase rate by player size'), use_container_width=True)
        st.caption("Bigger screens (4K, full HD) lead to more purchases than small mobile players.")

# ── Tab 3: Verified Deals + Curated Packages ────────────────────────────────
with tab3:
    st.header("Outcome-Verified Deals")
    st.caption("Every Magnite deal graded by real purchases from exposed audiences — Publisher Deals, Marketplace (curated) Deals and Auction Packages.")

    deals = q(f"SELECT * FROM {DB}.DEMO_OUTPUT_DEAL_OUTCOMES ORDER BY YIELD_INDEX DESC")
    deals['DEAL_LABEL'] = deals['DEAL_NAME'] + ' (' + deals['FEED'].str.replace('DVPLUS', 'DV+').str.replace('STREAMING', 'Streaming') + ')'
    c1, c2, c3 = st.columns(3)
    c1.metric("Deals Graded", len(deals))
    c2.metric("Grade A Deals", int(deals['OUTCOME_GRADE'].str.startswith('A').sum()))
    c3.metric("Best Deal Yield", f"{deals['YIELD_INDEX'].max():.2f}x", delta=deals.iloc[0]['DEAL_NAME'])

    dchart = alt.Chart(deals).mark_bar().encode(
        x=alt.X('YIELD_INDEX:Q', title='Yield index (1.0 = average)'),
        y=alt.Y('DEAL_LABEL:N', sort='-x', title=''),
        color=alt.Color('DEAL_TYPE:N', title='Deal type'),
        tooltip=['DEAL_ID', 'DEAL_NAME', 'DEAL_TYPE', 'PURCHASE_RATE_PCT', 'YIELD_INDEX', 'AVG_PURCHASE_VALUE', 'OUTCOME_GRADE']
    ).properties(height=480, title='Deal scorecard — purchase yield by deal')
    rule = alt.Chart(pd.DataFrame({'x': [1.0]})).mark_rule(strokeDash=[4, 4], color='black').encode(x='x:Q')
    st.altair_chart(dchart + rule, use_container_width=True)
    st.caption("Dashed line = average. Not every curated deal beats average — outcome data shows which ones really do.")
    st.dataframe(deals[['DEAL_ID', 'DEAL_NAME', 'DEAL_TYPE', 'FEED', 'TOTAL_IMPRESSIONS', 'MATCHED_IMPRESSIONS', 'PURCHASES',
                        'PURCHASE_RATE_PCT', 'YIELD_INDEX', 'AVG_PURCHASE_VALUE', 'VALUE_PER_1K_IMPS', 'OUTCOME_GRADE']],
                 use_container_width=True)

    st.markdown("---")
    st.subheader("Affinity Outcome-Verified Curated Packages")
    st.caption("New Marketplace deal ideas built from what actually drives purchases. Each one compared with run of network.")
    pk = q(f"SELECT * FROM {DB}.DEMO_OUTPUT_CURATED_PACKAGES ORDER BY LIFT_VS_AVG DESC")
    pchart = alt.Chart(pk).mark_bar().encode(
        x=alt.X('LIFT_VS_AVG:Q', title='Lift vs average'),
        y=alt.Y('PACKAGE_NAME:N', sort='-x', title=''),
        color=alt.condition(alt.datum.LIFT_VS_AVG >= 1.4, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['PACKAGE_NAME', 'DESCRIPTION', 'PURCHASE_RATE_PCT', 'LIFT_VS_AVG', 'REACH_INDIVIDUALS', 'SUGGESTED_PRICE_TIER']
    ).properties(height=300, title='Curated packages — purchase lift')
    st.altair_chart(pchart, use_container_width=True)
    st.caption("Green = premium-tier package (40%+ above average).")
    st.dataframe(pk, use_container_width=True)

# ── Tab 4: Buyer Outcomes ───────────────────────────────────────────────────
with tab4:
    st.header("Buyer Outcome Reports — Proving Exposure Drove Sales")
    st.caption("For each buyer seat: the impressions it won on Magnite and the purchases that followed. This is the 'attribute outcomes to exposure' promise of log-level data.")

    buyers = q(f"SELECT * FROM {DB}.DEMO_OUTPUT_BUYER_OUTCOMES ORDER BY LIFT_VS_AVG DESC")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Buyer Seats", len(buyers))
    c2.metric("Outperforming", int((buyers['OUTCOME_STATUS'] == 'Outperforming').sum()))
    c3.metric("Needs Optimization", int((buyers['OUTCOME_STATUS'] == 'Needs optimization').sum()))
    c4.metric("Attributed Sales", f"${buyers['ATTRIBUTED_PURCHASE_VALUE'].sum()/1e6:.2f}M")

    bchart = alt.Chart(buyers).mark_bar().encode(
        x=alt.X('BUYER_SEAT_CODE:N', sort='-y', title='Buyer seat', axis=alt.Axis(labels=False)),
        y=alt.Y('LIFT_VS_AVG:Q', title='Purchase lift vs average'),
        color=alt.Color('OUTCOME_STATUS:N', scale=alt.Scale(domain=['Outperforming', 'On par', 'Needs optimization'],
                                                            range=['#2ecc71', '#95a5a6', '#e74c3c']), title=''),
        tooltip=['DSP_ID', 'BUYER_ID', 'BUYER_SEAT_CODE', 'PURCHASE_RATE_PCT', 'LIFT_VS_AVG', 'ATTRIBUTED_PURCHASE_VALUE', 'BEST_SUPPLY']
    ).properties(height=320, title='Purchase lift by buyer seat')
    st.altair_chart(bchart, use_container_width=True)
    st.caption("Same supply, very different results. Red seats are good candidates for a curated package or deal recommendation.")

    st.subheader("Outcome Report Card")
    seat = st.selectbox("Choose a buyer seat", buyers['BUYER_SEAT_CODE'].tolist())
    r = buyers[buyers['BUYER_SEAT_CODE'] == seat].iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Impressions Won", f"{int(r['IMPRESSIONS_WON']):,}", delta=f"{r['CTV_SHARE_PCT']}% CTV")
    c2.metric("Purchasers Reached", f"{int(r['PURCHASERS']):,}")
    c3.metric("Purchase Rate", f"{r['PURCHASE_RATE_PCT']}%", delta=f"{r['LIFT_VS_AVG']}x vs avg")
    c4.metric("Attributed Sales", f"${r['ATTRIBUTED_PURCHASE_VALUE']:,.0f}")
    c5.metric("Best Supply", str(r['BEST_SUPPLY']))
    st.caption(f"{r['DSP_ID']} · {r['BUYER_ID']} · status: {r['OUTCOME_STATUS']}")
    st.dataframe(buyers, use_container_width=True, height=300)

# ── Tab 5: Pricing Rules ────────────────────────────────────────────────────
with tab5:
    st.header("Pricing Rules — Purchase-Backed Price Guidance")
    st.caption("BOOST = price higher (this inventory sells). SUPPRESS = price lower. Built only from fields known when the impression is sold.")

    rules = q(f"SELECT * FROM {DB}.DEMO_OUTPUT_PRICING_RULES ORDER BY SHRUNK_LIFT DESC")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rules", len(rules))
    c2.metric("BOOST", int((rules['RULE_ACTION'] == 'BOOST').sum()), delta="Price up")
    c3.metric("SUPPRESS", int((rules['RULE_ACTION'] == 'SUPPRESS').sum()), delta="Price down", delta_color="inverse")
    c4.metric("NEUTRAL", int((rules['RULE_ACTION'] == 'NEUTRAL').sum()))

    c1, c2 = st.columns(2)
    action_filter = c1.selectbox("Action", ["All", "BOOST", "NEUTRAL", "SUPPRESS"])
    dim_filter = c2.selectbox("Dimension", ["All"] + sorted(rules['DIM'].unique().tolist()))
    f = rules.copy()
    if action_filter != "All":
        f = f[f['RULE_ACTION'] == action_filter]
    if dim_filter != "All":
        f = f[f['DIM'] == dim_filter]
    st.dataframe(f[['RULE_ID', 'PREDICATE', 'DIM', 'SUPPORT', 'RAW_LIFT', 'SHRUNK_LIFT', 'PRICE_MULTIPLIER', 'CI_LOWER', 'CI_UPPER', 'RULE_ACTION']],
                 use_container_width=True, height=350)

    hist = alt.Chart(rules).mark_bar().encode(
        x=alt.X('SHRUNK_LIFT:Q', bin=alt.Bin(maxbins=30), title='Lift over average (after small-sample adjustment)'),
        y=alt.Y('count()', title='Rules'),
        color=alt.Color('RULE_ACTION:N', scale=ACTION_COLORS)
    ).properties(height=280, title='Lift distribution — Magnite pricing rules')
    st.altair_chart(hist, use_container_width=True)
    st.caption("Green = BOOST, red = SUPPRESS, gray = NEUTRAL (not enough evidence to act). Small segments are pulled toward 1.0 so noise doesn't drive price.")

    st.markdown("---")
    st.subheader("Price Tiers by Supply × Device")
    st.caption("Every app/site × device segment placed in a price tier, with a suggested price multiplier.")
    tiers = q(f"SELECT * FROM {DB}.DEMO_OUTPUT_PRICING_TIERS ORDER BY YIELD_INDEX DESC")
    ts = tiers.groupby('PRICE_TIER').agg(SEGMENTS=('SUPPLY_NAME', 'count'), AVG_MULT=('SUGGESTED_PRICE_MULTIPLIER', 'mean')).reset_index()
    icons = {'1 - Premium': '🟢', '2 - Plus': '🟢', '3 - Standard': '🟡', '4 - Value': '🔴'}
    cols = st.columns(len(ts))
    for i, (_, row) in enumerate(ts.iterrows()):
        cols[i].metric(f"{icons.get(row['PRICE_TIER'], '')} {row['PRICE_TIER']}", f"{int(row['SEGMENTS'])} segments", f"Avg multiplier {row['AVG_MULT']:.2f}x")
    st.dataframe(tiers, use_container_width=True, height=300)

# ── Tab 6: Cross-Screen ─────────────────────────────────────────────────────
with tab6:
    st.header("Cross-Screen — CTV + Display Together")
    st.caption("Affinity links the same person and household across Magnite's Streaming and DV+ feeds, so we can see what seeing ads on both screens does.")

    level = st.radio("Measure at", ["Household", "Individual"], horizontal=True)
    xs = q(f"SELECT * FROM {DB}.DEMO_OUTPUT_CROSS_SCREEN")
    xs = xs[xs['LEVEL'] == level]
    both = xs[xs['EXPOSURE_GROUP'] == 'CTV + Display'].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Cross-Screen {level}s", f"{int(both['UNITS']):,}")
    c2.metric("CTV Lift (both vs CTV only)", f"{both['CTV_LIFT_VS_SINGLE_SCREEN']}x")
    c3.metric("Display Lift (both vs display only)", f"{both['DISPLAY_LIFT_VS_SINGLE_SCREEN']}x")

    c1, c2 = st.columns(2)
    with c1:
        d1 = xs[xs['EXPOSURE_GROUP'].isin(['CTV only', 'CTV + Display'])]
        st.altair_chart(alt.Chart(d1).mark_bar().encode(
            x=alt.X('EXPOSURE_GROUP:N', title='', sort=['CTV only', 'CTV + Display']),
            y=alt.Y('CTV_PURCHASE_RATE_PCT:Q', title='Purchase rate on CTV impressions %'),
            color=alt.Color('EXPOSURE_GROUP:N', scale=alt.Scale(domain=['CTV only', 'CTV + Display'], range=['#95a5a6', '#2ecc71']), legend=None),
            tooltip=['EXPOSURE_GROUP', 'CTV_PURCHASE_RATE_PCT', 'UNITS']
        ).properties(height=300, title='CTV ads work better when display is in the mix'), use_container_width=True)
    with c2:
        d2 = xs[xs['EXPOSURE_GROUP'].isin(['Display only', 'CTV + Display'])]
        st.altair_chart(alt.Chart(d2).mark_bar().encode(
            x=alt.X('EXPOSURE_GROUP:N', title='', sort=['Display only', 'CTV + Display']),
            y=alt.Y('DISPLAY_PURCHASE_RATE_PCT:Q', title='Purchase rate on display impressions %'),
            color=alt.Color('EXPOSURE_GROUP:N', scale=alt.Scale(domain=['Display only', 'CTV + Display'], range=['#95a5a6', '#2ecc71']), legend=None),
            tooltip=['EXPOSURE_GROUP', 'DISPLAY_PURCHASE_RATE_PCT', 'UNITS']
        ).properties(height=300, title='Display ads work better when CTV is in the mix'), use_container_width=True)
    st.caption("Like-for-like: each chart compares the same kind of impression. Green = people/households reached on both screens.")
    st.dataframe(xs.drop(columns=['LEVEL']), use_container_width=True)

# ── Tab 7: ML Models ────────────────────────────────────────────────────────
with tab7:
    st.header("Snowflake ML Models — Magnite")
    st.caption("Two models trained on 1.77M matched impressions with Snowflake ML. Affinity purchases are the answer key; Magnite log fields plus Affinity's purchase score are the inputs.")

    registry = q("SELECT * FROM AFFINITY_DEMO.ML.MODEL_REGISTRY WHERE MODEL_NAME LIKE 'MAGNITE%' ORDER BY MODEL_NAME DESC")
    for _, row in registry.iterrows():
        with st.expander(f"**{row['MODEL_NAME']}** — {row['MODEL_TYPE']}", expanded=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {row['DESCRIPTION']}")
            c1.markdown(f"**Target:** {row['TARGET_TYPE']}")
            c2.markdown(f"**Training data:** {row['TRAINING_DATA']}")
            c2.markdown(f"**Features:** {row['FEATURES']}")
            st.success(f"**Key metric:** {row['KEY_METRIC']}")

    st.subheader("Model Performance — Decile Lift (holdout, unseen data)")
    st.caption("Holdout impressions split into 10 equal groups by model score. Green = top 3 groups, the inventory to price as premium.")
    deciles = q("SELECT * FROM AFFINITY_DEMO.ML.MAGNITE_VALIDATION_DECILES ORDER BY DECILE")
    st.altair_chart(alt.Chart(deciles).mark_bar().encode(
        x=alt.X('DECILE:O', title='Decile (1 = highest scored)'),
        y=alt.Y('PURCHASE_RATE_PCT:Q', title='Purchase rate %'),
        color=alt.condition(alt.datum.DECILE <= 3, alt.value('#2ecc71'), alt.value('#bdc3c7')),
        tooltip=['DECILE', 'PURCHASE_RATE_PCT', 'CUMUL_CAPTURE_PCT', 'DECILE_LIFT']
    ).properties(height=320, title='Purchase rate by ML score decile — Magnite Yield Classifier'), use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Top Decile Lift", f"{deciles.iloc[0]['DECILE_LIFT']}x")
    c2.metric("Top 30% Capture", f"{deciles.iloc[2]['CUMUL_CAPTURE_PCT']}% of purchases")
    c3.metric("Top vs Bottom", f"{deciles.iloc[0]['PURCHASE_RATE_PCT']/max(deciles.iloc[9]['PURCHASE_RATE_PCT'], 0.01):.0f}x separation")

    st.markdown("---")
    st.subheader("Feature Importance")
    st.caption("Longer bar = more influence. Who is buying (buyer seat), where the ad runs (app/site) and Affinity's purchase score lead both models.")
    fi = q("SELECT * FROM AFFINITY_DEMO.ML.MAGNITE_FEATURE_IMPORTANCE ORDER BY MODEL, RANK")
    c1, c2 = st.columns(2)
    for col, model, color, label in [(c1, 'MAGNITE_YIELD_CLASSIFIER', '#8e44ad', '**Yield Classifier** — *which impressions lead to a purchase*'),
                                     (c2, 'MAGNITE_SPEND_CLASSIFIER', '#e67e22', '**Spend Classifier** — *how much buyers spend*')]:
        with col:
            st.markdown(label)
            st.altair_chart(alt.Chart(fi[fi['MODEL'] == model]).mark_bar(color=color).encode(
                x=alt.X('IMPORTANCE_SCORE:Q', title='Importance'),
                y=alt.Y('FEATURE:N', sort='-x', title=''),
                tooltip=['FEATURE', 'IMPORTANCE_SCORE', 'RANK']
            ).properties(height=340), use_container_width=True)

    st.markdown("---")
    st.subheader("Holdout Check — Does the Model Hold Up on New Data?")
    st.caption("Training and holdout rates match (no overfitting). Within the holdout, the model's top 30% converts about 5x better than the rest.")
    ho = q("SELECT * FROM AFFINITY_DEMO.ML.MAGNITE_HOLDOUT_RESULTS ORDER BY SET_NAME")
    cols = st.columns(len(ho))
    for i, (_, row) in enumerate(ho.iterrows()):
        with cols[i]:
            st.markdown(f"**{row['SET_NAME'][3:]}**")
            st.metric("Purchase Rate", f"{row['PURCHASE_RATE_PCT']}%")
            st.metric("Sales per 1K Impressions", f"${row['VALUE_PER_1K_IMPS']:,.0f}")
            st.metric("Impressions", f"{int(row['IMPRESSIONS']):,}")
