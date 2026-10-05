"""
Logistics KPI Automation & Multi-Carrier Analytics Platform
Module: High-Density Synthetic Logistics Event Generator (data_generator.py)

Generates realistic e-commerce logistics, freight quoting, and multi-carrier
shipment events with accurate statistical distributions (Log-Normal transit times,
volumetric weight discrepancies, SLA breach tail-risks, and carrier margin leakage).
"""

import os
import argparse
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# 1. CANONICAL MASTER CATALOGS
# -----------------------------------------------------------------------------

CARRIERS_CATALOG = [
    {
        "carrier_id": "CAR-001",
        "carrier_name": "FedEx Express Mexico",
        "carrier_code": "FEDEX_EXP",
        "contract_tier": "Tier-1 Global",
        "service_level": "Express",
        "base_sla_days": 1,
        "base_rate_per_kg": 45.50,
        "historical_otd_target": 0.95,
        "weight_audit_freq": 0.25,
    },
    {
        "carrier_id": "CAR-002",
        "carrier_name": "DHL Express Logistics",
        "carrier_code": "DHL_EXP",
        "contract_tier": "Tier-1 Global",
        "service_level": "Express",
        "base_sla_days": 1,
        "base_rate_per_kg": 48.00,
        "historical_otd_target": 0.96,
        "weight_audit_freq": 0.30,
    },
    {
        "carrier_id": "CAR-003",
        "carrier_name": "Estafeta Terrestre",
        "carrier_code": "ESTAFETA_TER",
        "contract_tier": "Tier-2 National",
        "service_level": "Standard",
        "base_sla_days": 3,
        "base_rate_per_kg": 26.50,
        "historical_otd_target": 0.88,
        "weight_audit_freq": 0.40,
    },
    {
        "carrier_id": "CAR-004",
        "carrier_name": "99Minutos SameDay / NextDay",
        "carrier_code": "99MIN_URBAN",
        "contract_tier": "Tier-2 Regional",
        "service_level": "Express Urban",
        "base_sla_days": 1,
        "base_rate_per_kg": 32.00,
        "historical_otd_target": 0.91,
        "weight_audit_freq": 0.15,
    },
    {
        "carrier_id": "CAR-005",
        "carrier_name": "Redpack Ground Logistics",
        "carrier_code": "REDPACK_ECO",
        "contract_tier": "Tier-3 Economy",
        "service_level": "Standard",
        "base_sla_days": 4,
        "base_rate_per_kg": 21.00,
        "historical_otd_target": 0.84,
        "weight_audit_freq": 0.35,
    },
    {
        "carrier_id": "CAR-006",
        "carrier_name": "Correos de Mexico (SEPOMEX)",
        "carrier_code": "CORREOS_ECO",
        "contract_tier": "Tier-3 Postal",
        "service_level": "Economy",
        "base_sla_days": 7,
        "base_rate_per_kg": 12.50,
        "historical_otd_target": 0.73,
        "weight_audit_freq": 0.10,
    },
]

GEOGRAPHY_CATALOG = [
    {"geo_id": "GEO-CDMX", "zone_code": "Z-01", "state_region": "Ciudad de Mexico", "zone_type": "Metro Core", "remote_surcharge": 0.0},
    {"geo_id": "GEO-GDL",  "zone_code": "Z-02", "state_region": "Jalisco (Guadalajara)", "zone_type": "Metro Core", "remote_surcharge": 0.0},
    {"geo_id": "GEO-MTY",  "zone_code": "Z-03", "state_region": "Nuevo Leon (Monterrey)", "zone_type": "Metro Core", "remote_surcharge": 0.0},
    {"geo_id": "GEO-QRO",  "zone_code": "Z-04", "state_region": "Queretaro Bajio", "zone_type": "Regional Hub", "remote_surcharge": 0.0},
    {"geo_id": "GEO-PUE",  "zone_code": "Z-05", "state_region": "Puebla Central", "zone_type": "Regional Hub", "remote_surcharge": 0.0},
    {"geo_id": "GEO-TIJ",  "zone_code": "Z-06", "state_region": "Baja California (Tijuana)", "zone_type": "Border Corridor", "remote_surcharge": 15.0},
    {"geo_id": "GEO-MID",  "zone_code": "Z-07", "state_region": "Yucatan (Merida)", "zone_type": "Southeast Corridor", "remote_surcharge": 18.0},
    {"geo_id": "GEO-CUN",  "zone_code": "Z-08", "state_region": "Quintana Roo (Cancun)", "zone_type": "Extended Remote", "remote_surcharge": 35.0},
    {"geo_id": "GEO-OAX",  "zone_code": "Z-09", "state_region": "Oaxaca Sierra", "zone_type": "Extended Remote", "remote_surcharge": 45.0},
    {"geo_id": "GEO-CHI",  "zone_code": "Z-10", "state_region": "Chihuahua Desert", "zone_type": "Extended Remote", "remote_surcharge": 40.0},
]

MERCHANTS_CATALOG = [
    {"merchant_id": "MCH-001", "merchant_name": "ElectroTech Mexico", "tier": "Enterprise", "category": "Consumer Electronics", "margin_markup_pct": 0.12},
    {"merchant_id": "MCH-002", "merchant_name": "Moda Urbana CDMX", "tier": "Enterprise", "category": "Fashion & Apparel", "margin_markup_pct": 0.14},
    {"merchant_id": "MCH-003", "merchant_name": "Suplementos Vitalis", "tier": "Mid-Market", "category": "Health & Nutrition", "margin_markup_pct": 0.18},
    {"merchant_id": "MCH-004", "merchant_name": "AutoPartes Express", "tier": "Enterprise", "category": "Automotive Aftermarket", "margin_markup_pct": 0.15},
    {"merchant_id": "MCH-005", "merchant_name": "Casa & Confort Deco", "tier": "Mid-Market", "category": "Home & Living", "margin_markup_pct": 0.20},
    {"merchant_id": "MCH-006", "merchant_name": "Belleza Radiante", "tier": "SMB", "category": "Beauty & Personal Care", "margin_markup_pct": 0.25},
    {"merchant_id": "MCH-007", "merchant_name": "Gamer Zone Latam", "tier": "Enterprise", "category": "Gaming & Tech", "margin_markup_pct": 0.13},
    {"merchant_id": "MCH-008", "merchant_name": "Organicos del Valle", "tier": "SMB", "category": "Gourmet & Organic Food", "margin_markup_pct": 0.24},
    {"merchant_id": "MCH-009", "merchant_name": "Zapateria Tradicion", "tier": "Mid-Market", "category": "Footwear", "margin_markup_pct": 0.19},
    {"merchant_id": "MCH-010", "merchant_name": "Herramientas Industriales Norte", "tier": "Mid-Market", "category": "Industrial Tools", "margin_markup_pct": 0.17},
]


# -----------------------------------------------------------------------------
# 2. HIGH-DENSITY EVENT GENERATOR ENGINE
# -----------------------------------------------------------------------------

class LogisticsDataGenerator:
    """
    Generates enterprise-scale multi-carrier logistics events with realistic
    stochastic noise, SLA distributions, and financial margin discrepancies.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def generate_date_dimension(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generates an exhaustive Kimball Date Dimension (dim_date)."""
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        records = []
        for dt in date_range:
            records.append({
                "date_id": int(dt.strftime("%Y%m%d")),
                "full_date": dt.date(),
                "year": dt.year,
                "quarter": dt.quarter,
                "month": dt.month,
                "month_name": dt.strftime("%B"),
                "week_of_year": int(dt.isocalendar().week),
                "day_of_month": dt.day,
                "day_of_week": dt.weekday() + 1,  # 1=Monday, 7=Sunday
                "day_name": dt.strftime("%A"),
                "is_weekend": 1 if dt.weekday() >= 5 else 0,
                "is_month_end": 1 if dt.is_month_end else 0,
            })
        return pd.DataFrame(records)

    def generate_dataset(
        self,
        num_shipments: int = 35000,
        num_quotes: int = 60000,
        days_history: int = 180
    ) -> Dict[str, pd.DataFrame]:
        """
        Generates the complete synthetic logistics data lakehouse tables.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_history)

        df_dim_date = self.generate_date_dimension(start_date, end_date + timedelta(days=30))
        df_dim_carriers = pd.DataFrame(CARRIERS_CATALOG)
        df_dim_geography = pd.DataFrame(GEOGRAPHY_CATALOG)
        df_dim_merchants = pd.DataFrame(MERCHANTS_CATALOG)

        # 1. Generate Carrier Quotes (fact_carrier_quotes)
        quotes_list = []
        for i in range(1, num_quotes + 1):
            quote_id = f"QTE-{i:07d}"
            merchant = random.choice(MERCHANTS_CATALOG)
            carrier = random.choice(CARRIERS_CATALOG)
            origin = random.choice(GEOGRAPHY_CATALOG)
            dest = random.choice(GEOGRAPHY_CATALOG)

            quote_dt = start_date + timedelta(seconds=random.randint(0, int(days_history * 86400)))
            declared_weight = round(float(np.random.gamma(shape=2.5, scale=1.2)), 2) + 0.20
            
            # Quoted rate based on carrier rate per kg + remote surcharge
            base_quote = carrier["base_rate_per_kg"] * declared_weight
            surcharge = dest["remote_surcharge"]
            quoted_rate = round(base_quote + surcharge + random.uniform(5.0, 25.0), 2)
            est_transit = carrier["base_sla_days"] + (2 if "Remote" in dest["zone_type"] else 0)

            quotes_list.append({
                "quote_id": quote_id,
                "merchant_id": merchant["merchant_id"],
                "carrier_id": carrier["carrier_id"],
                "origin_geo_id": origin["geo_id"],
                "dest_geo_id": dest["geo_id"],
                "quote_date_id": int(quote_dt.strftime("%Y%m%d")),
                "quote_timestamp": quote_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "declared_weight_kg": declared_weight,
                "quoted_rate": quoted_rate,
                "estimated_transit_days": est_transit,
                "was_converted_to_shipment": 0,  # Will update for converted
            })

        df_quotes = pd.DataFrame(quotes_list)

        # 2. Generate Shipments (fact_shipments)
        shipments_list = []
        num_converted = min(num_shipments, len(df_quotes))
        converted_indices = np.random.choice(len(df_quotes), size=num_converted, replace=False)
        df_quotes.loc[converted_indices, "was_converted_to_shipment"] = 1

        for idx_num, quote_idx in enumerate(converted_indices, 1):
            q_row = df_quotes.iloc[quote_idx]
            shipment_id = f"SHP-{idx_num:07d}"
            tracking_number = f"TRK{random.randint(100000000, 999999999)}"
            
            carrier_info = next(c for c in CARRIERS_CATALOG if c["carrier_id"] == q_row["carrier_id"])
            merchant_info = next(m for m in MERCHANTS_CATALOG if m["merchant_id"] == q_row["merchant_id"])
            dest_info = next(g for g in GEOGRAPHY_CATALOG if g["geo_id"] == q_row["dest_geo_id"])

            order_dt = datetime.strptime(q_row["quote_timestamp"], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=random.randint(5, 120))
            order_date_id = int(order_dt.strftime("%Y%m%d"))

            # Promised SLA calculation
            promised_sla_days = int(q_row["estimated_transit_days"])
            promised_delivery_dt = order_dt + timedelta(days=promised_sla_days)
            promised_date_id = int(promised_delivery_dt.strftime("%Y%m%d"))

            # Weight Audit Discrepancy (Volumetric Re-weigh by Carrier)
            declared_weight = q_row["declared_weight_kg"]
            if random.random() < carrier_info["weight_audit_freq"]:
                # Carrier re-weighed and found volumetric weight discrepancy
                weight_discrepancy_factor = random.uniform(1.20, 2.10)
                billed_weight = round(declared_weight * weight_discrepancy_factor, 2)
            else:
                billed_weight = declared_weight

            # Financials: Freight markup & carrier billing
            quoted_shipping_fee = q_row["quoted_rate"]
            # Gross revenue charged to merchant = quoted rate * (1 + merchant markup)
            gross_revenue = round(quoted_shipping_fee * (1.0 + merchant_info["margin_markup_pct"]), 2)
            
            # Carrier cost billed to Logistics Gateway Practice/Multi-Carrier Logistics Practice:
            # If carrier audited the weight or added zone surcharge, cost increases!
            carrier_cost_base = carrier_info["base_rate_per_kg"] * billed_weight + dest_info["remote_surcharge"]
            # Occasional fuel or handling variance (carrier margin leakage)
            cost_noise = random.uniform(-2.0, 8.0) if random.random() < 0.30 else 0.0
            billed_carrier_cost = round(max(15.0, carrier_cost_base + cost_noise), 2)
            
            # Net margin for platform
            net_margin = round(gross_revenue - billed_carrier_cost, 2)
            cost_variance = round(billed_carrier_cost - (carrier_info["base_rate_per_kg"] * declared_weight + dest_info["remote_surcharge"]), 2)

            # Actual Transit Time simulation (Weibull / Log-Normal distribution)
            # Probability of SLA hit depends on carrier historical target
            otd_target = carrier_info["historical_otd_target"]
            is_otd = random.random() < otd_target
            
            if is_otd:
                actual_transit_days = max(1, random.randint(1, promised_sla_days))
                delivery_status = "DELIVERED"
                is_sla_breached = 0
                is_exception = 0
            else:
                # Long tail delay or exception
                delay_extra = random.randint(1, 6)
                actual_transit_days = promised_sla_days + delay_extra
                is_sla_breached = 1
                
                # Probability of severe exception
                exc_roll = random.random()
                if exc_roll < 0.08:
                    delivery_status = "RETURNED_TO_SENDER"
                    is_exception = 1
                elif exc_roll < 0.12:
                    delivery_status = "LOST_IN_TRANSIT"
                    is_exception = 1
                else:
                    delivery_status = "DELIVERED_LATE"
                    is_exception = 0

            actual_delivery_dt = order_dt + timedelta(days=actual_transit_days, hours=random.randint(2, 18))
            actual_date_id = int(actual_delivery_dt.strftime("%Y%m%d"))

            shipments_list.append({
                "shipment_id": shipment_id,
                "quote_id": q_row["quote_id"],
                "tracking_number": tracking_number,
                "merchant_id": q_row["merchant_id"],
                "carrier_id": q_row["carrier_id"],
                "origin_geo_id": q_row["origin_geo_id"],
                "dest_geo_id": q_row["dest_geo_id"],
                "order_date_id": order_date_id,
                "order_timestamp": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "promised_delivery_date_id": promised_date_id,
                "actual_delivery_date_id": actual_date_id,
                "actual_delivery_timestamp": actual_delivery_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "service_level": carrier_info["service_level"],
                "delivery_status": delivery_status,
                "declared_weight_kg": declared_weight,
                "billed_weight_kg": billed_weight,
                "is_weight_discrepancy": 1 if billed_weight > declared_weight else 0,
                "quoted_shipping_fee": quoted_shipping_fee,
                "billed_carrier_cost": billed_carrier_cost,
                "carrier_cost_variance": cost_variance,
                "gross_revenue": gross_revenue,
                "net_margin": net_margin,
                "transit_time_days": actual_transit_days,
                "promised_sla_days": promised_sla_days,
                "is_sla_breached": is_sla_breached,
                "is_exception": is_exception,
            })

        df_shipments = pd.DataFrame(shipments_list)

        return {
            "dim_date": df_dim_date,
            "dim_carriers": df_dim_carriers,
            "dim_geography": df_dim_geography,
            "dim_merchants": df_dim_merchants,
            "fact_carrier_quotes": df_quotes,
            "fact_shipments": df_shipments,
        }

    def export_to_parquet(self, tables: Dict[str, pd.DataFrame], output_dir: str = "data/raw"):
        """Exports generated tables as clean, compressed Parquet files."""
        os.makedirs(output_dir, exist_ok=True)
        for table_name, df in tables.items():
            file_path = os.path.join(output_dir, f"{table_name}.parquet")
            df.to_parquet(file_path, engine="pyarrow", compression="snappy", index=False)
            print(f"[Data Generator] Table '{table_name}' exported: {len(df):,} rows -> {file_path}")


# -----------------------------------------------------------------------------
# 3. CLI ENTRYPOINT
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Logistics Event Generator")
    parser.add_argument("--shipments", type=int, default=35000, help="Number of shipments to generate")
    parser.add_argument("--quotes", type=int, default=50000, help="Number of quotes to generate")
    parser.add_argument("--days", type=int, default=180, help="Historical days range")
    parser.add_argument("--output", type=str, default="data/raw", help="Output directory for raw Parquet files")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    print("=" * 80)
    print(">> LOGISTICS & SHIPPING HIGH-DENSITY EVENT GENERATOR")
    print(f">> Target: {args.shipments:,} shipments | {args.quotes:,} quotes | {args.days} days")
    print("=" * 80)

    generator = LogisticsDataGenerator(seed=args.seed)
    tables = generator.generate_dataset(
        num_shipments=args.shipments,
        num_quotes=args.quotes,
        days_history=args.days
    )
    generator.export_to_parquet(tables, output_dir=args.output)
    print(">> [Data Generator] High-Density Dataset Generation Complete.")


if __name__ == "__main__":
    main()

