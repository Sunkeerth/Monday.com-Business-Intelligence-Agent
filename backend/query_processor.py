import pandas as pd
import monday_client
import data_cleaner

def interpret_query(query, trace):
    trace.append("Interpret query: " + query)
    query_lower = query.lower()

    fetch_deals = any(k in query_lower for k in ["deal", "pipeline", "sector", "revenue", "won", "open"])
    fetch_wo = any(k in query_lower for k in ["work order", "wo", "execution", "billed"])

    deals_df = None
    wo_df = None

    if fetch_deals:
        trace.append("Fetching Deals board...")
        deals_raw = monday_client.get_deals()
        deals_df = pd.DataFrame(deals_raw)
        deals_df = data_cleaner.clean_deals(deals_df)
        trace.append(f"Fetched {len(deals_df)} deals.")

    if fetch_wo:
        trace.append("Fetching Work Orders board...")
        wo_raw = monday_client.get_work_orders()
        wo_df = pd.DataFrame(wo_raw)
        wo_df = data_cleaner.clean_work_orders(wo_df)
        trace.append(f"Fetched {len(wo_df)} work orders.")

    chart_data = None

    # --- Helper to find column names by keyword ---
    def find_column(df, keywords):
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None

    # --- Answer specific questions ---
    if "pipeline" in query_lower and "sector" in query_lower:
        sector = extract_sector(query_lower)
        if sector and deals_df is not None:
            sector_col = find_column(deals_df, ["sector"])
            status_col = find_column(deals_df, ["status"])
            value_col = find_column(deals_df, ["value", "amount"])
            stage_col = find_column(deals_df, ["stage"])

            if sector_col and status_col:
                open_deals = deals_df[deals_df[status_col].str.lower().isin(["open", "on hold"])]
                sector_deals = open_deals[open_deals[sector_col].str.lower() == sector.lower()]
                total_value = sector_deals[value_col].sum() if value_col else 0
                count = len(sector_deals)
                if count > 0 and stage_col:
                    stage_counts = sector_deals[stage_col].value_counts()
                    chart_data = {
                        "labels": stage_counts.index.tolist(),
                        "values": stage_counts.values.tolist()
                    }
                return f"Found {count} open deals in {sector} sector with total value ₹{total_value:,.0f}.", trace, chart_data

    if "revenue" in query_lower and "won" in query_lower and deals_df is not None:
        status_col = find_column(deals_df, ["status"])
        value_col = find_column(deals_df, ["value", "amount"])
        sector_col = find_column(deals_df, ["sector"])

        if status_col and value_col:
            won_deals = deals_df[deals_df[status_col].str.lower() == "won"]
            total = won_deals[value_col].sum()
            if sector_col and len(won_deals) > 0:
                sector_revenue = won_deals.groupby(sector_col)[value_col].sum()
                chart_data = {
                    "labels": sector_revenue.index.tolist(),
                    "values": sector_revenue.values.tolist()
                }
            return f"Total revenue from won deals: ₹{total:,.0f}.", trace, chart_data

    if "stuck" in query_lower or "on hold" in query_lower:
        if deals_df is not None:
            stage_col = find_column(deals_df, ["stage"])
            sector_col = find_column(deals_df, ["sector"])

            if stage_col:
                stuck = deals_df[deals_df[stage_col].str.contains("Stuck|On Hold|Hold", case=False, na=False)]
                if sector_col and len(stuck) > 0:
                    sector_counts = stuck[sector_col].value_counts()
                    chart_data = {
                        "labels": sector_counts.index.tolist(),
                        "values": sector_counts.values.tolist()
                    }
                return f"Found {len(stuck)} stuck/on-hold deals.", trace, chart_data

    if "work order" in query_lower and "sector" in query_lower and wo_df is not None:
        sector = extract_sector(query_lower)
        sector_col = find_column(wo_df, ["sector"])
        amount_col = find_column(wo_df, ["amount", "value"])
        status_col = find_column(wo_df, ["status"])

        if sector and sector_col:
            sector_wos = wo_df[wo_df[sector_col].str.lower() == sector.lower()]
            total_value = sector_wos[amount_col].sum() if amount_col else 0
            count = len(sector_wos)
            if status_col and count > 0:
                status_counts = sector_wos[status_col].value_counts()
                chart_data = {
                    "labels": status_counts.index.tolist(),
                    "values": status_counts.values.tolist()
                }
            return f"Found {count} work orders in {sector} sector with total value ₹{total_value:,.0f}.", trace, chart_data

    if "help" in query_lower:
        return ("I can answer questions like:\n"
                "- How's our pipeline looking for the energy sector this quarter?\n"
                "- What is the total revenue from won deals?\n"
                "- How many deals are stuck?\n"
                "- Show me work orders in Mining sector."), trace, None

    return "Sorry, I couldn't understand your question. Try asking about pipeline, revenue, or stuck deals.", trace, None

def extract_sector(query):
    sectors = ["mining", "powerline", "renewables", "railways", "construction", "dsp", "tender", "others"]
    for s in sectors:
        if s in query:
            return s
    return None