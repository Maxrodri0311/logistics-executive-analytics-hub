"""
Logistics KPI Automation & Multi-Carrier Analytics Platform
Module: Comprehensive Pytest Verification Suite (test_pipeline.py)

Validates data integrity, foreign key constraints, financial logic consistency,
SLA breach definitions, and Excel workbook output generation.
"""

import os
import sys
import pytest
import openpyxl

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_generator import LogisticsDataGenerator
from src.dimensional_model import DimensionalModelEngine
from src.excel_builder import ExecutiveExcelBuilder


@pytest.fixture(scope="session")
def pipeline_data(tmp_path_factory):
    """Fixture that generates test data and initializes DuckDB schema."""
    temp_dir = tmp_path_factory.mktemp("test_analytics_data")
    raw_dir = os.path.join(temp_dir, "raw")
    proc_dir = os.path.join(temp_dir, "processed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    # Generate small deterministic dataset
    gen = LogisticsDataGenerator(seed=42)
    tables = gen.generate_dataset(num_shipments=500, num_quotes=800, days_history=30)
    gen.export_to_parquet(tables, output_dir=raw_dir)

    # Initialize DuckDB Engine
    engine = DimensionalModelEngine(raw_data_dir=raw_dir, processed_data_dir=proc_dir)
    engine.initialize_schema()
    engine.export_processed_parquet()

    return {
        "engine": engine,
        "raw_dir": raw_dir,
        "proc_dir": proc_dir,
        "temp_dir": temp_dir
    }


def test_data_generator_output_integrity(pipeline_data):
    """Validates that the data generator exports non-empty dataframes with valid schemas."""
    engine = pipeline_data["engine"]
    
    # Check count of shipments and quotes
    shipments_count = engine.conn.execute("SELECT COUNT(*) FROM fact_shipments").fetchone()[0]
    quotes_count = engine.conn.execute("SELECT COUNT(*) FROM fact_carrier_quotes").fetchone()[0]
    
    assert shipments_count == 500, f"Expected 500 shipments, got {shipments_count}"
    assert quotes_count == 800, f"Expected 800 quotes, got {quotes_count}"


def test_foreign_key_referential_integrity(pipeline_data):
    """Ensures zero orphaned foreign keys in fact_shipments against all dimensions."""
    engine = pipeline_data["engine"]
    
    # 1. Carrier FK check
    orphaned_carriers = engine.conn.execute("""
        SELECT COUNT(*) FROM fact_shipments s
        LEFT JOIN dim_carriers c ON s.carrier_id = c.carrier_id
        WHERE c.carrier_id IS NULL
    """).fetchone()[0]
    assert orphaned_carriers == 0, "Detected orphaned carrier_id foreign keys!"

    # 2. Merchant FK check
    orphaned_merchants = engine.conn.execute("""
        SELECT COUNT(*) FROM fact_shipments s
        LEFT JOIN dim_merchants m ON s.merchant_id = m.merchant_id
        WHERE m.merchant_id IS NULL
    """).fetchone()[0]
    assert orphaned_merchants == 0, "Detected orphaned merchant_id foreign keys!"

    # 3. Geography FK check (Origin & Destination)
    orphaned_origin_geo = engine.conn.execute("""
        SELECT COUNT(*) FROM fact_shipments s
        LEFT JOIN dim_geography g ON s.origin_geo_id = g.geo_id
        WHERE g.geo_id IS NULL
    """).fetchone()[0]
    assert orphaned_origin_geo == 0, "Detected orphaned origin_geo_id foreign keys!"

    orphaned_dest_geo = engine.conn.execute("""
        SELECT COUNT(*) FROM fact_shipments s
        LEFT JOIN dim_geography g ON s.dest_geo_id = g.geo_id
        WHERE g.geo_id IS NULL
    """).fetchone()[0]
    assert orphaned_dest_geo == 0, "Detected orphaned dest_geo_id foreign keys!"


def test_financial_calculation_consistency(pipeline_data):
    """Validates financial mathematics: net margin = gross revenue - billed carrier cost."""
    engine = pipeline_data["engine"]
    
    discrepant_margins = engine.conn.execute("""
        SELECT COUNT(*) FROM fact_shipments
        WHERE ABS(net_margin - (gross_revenue - billed_carrier_cost)) > 0.05
    """).fetchone()[0]
    
    assert discrepant_margins == 0, f"Found {discrepant_margins} rows with invalid net margin arithmetic!"


def test_sla_breach_logic_consistency(pipeline_data):
    """Verifies that is_sla_breached flag strictly adheres to transit time vs promised SLA."""
    engine = pipeline_data["engine"]
    
    invalid_sla_flags = engine.conn.execute("""
        SELECT COUNT(*) FROM fact_shipments
        WHERE (transit_time_days > promised_sla_days AND is_sla_breached = 0)
           OR (transit_time_days <= promised_sla_days AND is_sla_breached = 1)
    """).fetchone()[0]
    
    assert invalid_sla_flags == 0, f"Found {invalid_sla_flags} rows with contradictory SLA breach flags!"


def test_scorecard_aggregation_accuracy(pipeline_data):
    """Validates that the aggregated carrier scorecard matches the total fact table volume."""
    engine = pipeline_data["engine"]
    df_scorecard = engine.get_carrier_scorecard()
    
    scorecard_volume = df_scorecard["total_shipments"].sum()
    fact_volume = engine.conn.execute("SELECT COUNT(*) FROM fact_shipments").fetchone()[0]
    
    assert scorecard_volume == fact_volume, f"Scorecard volume ({scorecard_volume}) does not match fact table ({fact_volume})"


def test_excel_dashboard_compilation(pipeline_data):
    """Tests the automated compilation and sheet structure of the Excel KPI dashboard."""
    engine = pipeline_data["engine"]
    temp_excel_path = os.path.join(pipeline_data["temp_dir"], "test_dashboard.xlsx")
    
    builder = ExecutiveExcelBuilder(output_path=temp_excel_path)
    # Inject test engine
    builder.engine = engine
    builder.generate_workbook()
    
    assert os.path.exists(temp_excel_path), "Excel workbook was not generated!"
    
    # Inspect workbook contents
    wb = openpyxl.load_workbook(temp_excel_path)
    expected_sheets = ["Executive Summary", "Regional SLA Matrix", "Merchant Insights", "Shipment Audit Feed"]
    for s in expected_sheets:
        assert s in wb.sheetnames, f"Expected sheet '{s}' missing in generated workbook!"
    
    # Verify Executive Summary title cell
    ws_summary = wb["Executive Summary"]
    assert "Multi-Carrier Logistics Practice / Logistics Gateway Practice" in str(ws_summary["A1"].value)
