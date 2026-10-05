"""
Core Analytical Engine: Modelado Dimensional Kimball (Star Schema) con DuckDB
Transforma el dataset crudo en Fact Table y Dimension Tables optimizadas
para consumo instantáneo en Power BI, Tableau y Excel C-Level.
"""

import os
import duckdb
import pandas as pd

def build_star_schema(db_path: str = "data/analytics.duckdb"):
    print("[CoreEngine] Inicializando motor DuckDB y construyendo Star Schema...")
    con = duckdb.connect(db_path)
    
    parquet_path = "data/raw_shipments.parquet"
    if not os.path.exists(parquet_path):
        from data_generator import generate_dataset
        generate_dataset(50000)

    con.execute(f"""
        CREATE OR REPLACE TABLE raw_data AS 
        SELECT * FROM read_parquet('{parquet_path}');
    """)

    # 1. Dimensión Carriers
    con.execute("""
        CREATE OR REPLACE TABLE dim_carriers AS
        SELECT DISTINCT 
            ROW_NUMBER() OVER (ORDER BY carrier_name) as carrier_key,
            carrier_name,
            CASE 
                WHEN carrier_name IN ('Carrier_Alpha', 'Carrier_Beta') THEN 'Tier-1 Strategic'
                ELSE 'Standard Partner'
            END as partnership_tier
        FROM raw_data;
    """)

    # 2. Dimensión Geografía
    con.execute("""
        CREATE OR REPLACE TABLE dim_geography AS
        SELECT DISTINCT 
            ROW_NUMBER() OVER (ORDER BY region) as geo_key,
            region,
            CASE 
                WHEN region IN ('North', 'Central') THEN 'Primary Hub'
                ELSE 'Secondary Hub'
            END as hub_type
        FROM raw_data;
    """)

    # 3. Fact Table Shipments
    con.execute("""
        CREATE OR REPLACE TABLE fact_shipments AS
        SELECT 
            r.shipment_id,
            r.merchant_id,
            c.carrier_key,
            g.geo_key,
            r.quoted_amount_usd,
            r.actual_cost_usd,
            r.gross_margin_usd,
            r.delivery_status,
            r.transit_days_target,
            r.actual_transit_days,
            CASE WHEN r.delivery_status = 'Delivered_On_Time' THEN 1 ELSE 0 END as is_on_time,
            CASE WHEN r.gross_margin_usd < 0 THEN 1 ELSE 0 END as is_negative_margin,
            r.created_at
        FROM raw_data r
        JOIN dim_carriers c ON r.carrier_name = c.carrier_name
        JOIN dim_geography g ON r.region = g.region;
    """)

    # Vistas analíticas C-Level
    kpi_summary = con.execute("""
        SELECT 
            c.carrier_name,
            COUNT(*) as total_shipments,
            ROUND(AVG(f.is_on_time) * 100, 2) as otd_sla_percentage,
            ROUND(SUM(f.quoted_amount_usd), 2) as total_revenue_usd,
            ROUND(SUM(f.gross_margin_usd), 2) as total_margin_usd,
            ROUND(AVG(f.gross_margin_usd / NULLIF(f.quoted_amount_usd, 0)) * 100, 2) as avg_margin_pct
        FROM fact_shipments f
        JOIN dim_carriers c ON f.carrier_key = c.carrier_key
        GROUP BY c.carrier_name
        ORDER BY total_shipments DESC;
    """).fetchdf()

    print("[CoreEngine] Star Schema generado exitosamente en DuckDB.")
    print("\n--- RESUMEN EJECUTIVO DE KPIS ---")
    print(kpi_summary.to_string(index=False))
    return kpi_summary

if __name__ == "__main__":
    build_star_schema()