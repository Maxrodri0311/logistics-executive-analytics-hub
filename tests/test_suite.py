"""
Batería de Pruebas Automatizadas de Integridad de Datos y Calidad de Esquema
"""

import os
import pytest
import duckdb
from src.data_generator import generate_dataset
from src.core_engine import build_star_schema

@pytest.fixture(scope="session")
def setup_data():
    df = generate_dataset(5000)
    summary = build_star_schema("data/test_analytics.duckdb")
    return df, summary

def test_dataset_record_count(setup_data):
    df, _ = setup_data
    assert len(df) == 5000
    assert "shipment_id" in df.columns
    assert "quoted_amount_usd" in df.columns

def test_zero_nulls_in_critical_fields(setup_data):
    df, _ = setup_data
    assert df["shipment_id"].isnull().sum() == 0
    assert df["carrier_name"].isnull().sum() == 0
    assert df["quoted_amount_usd"].isnull().sum() == 0

def test_star_schema_integrity():
    con = duckdb.connect("data/test_analytics.duckdb")
    fact_count = con.execute("SELECT COUNT(*) FROM fact_shipments").fetchone()[0]
    dim_c_count = con.execute("SELECT COUNT(*) FROM dim_carriers").fetchone()[0]
    dim_g_count = con.execute("SELECT COUNT(*) FROM dim_geography").fetchone()[0]
    
    assert fact_count == 5000
    assert dim_c_count > 0
    assert dim_g_count > 0

def test_sla_bounds():
    con = duckdb.connect("data/test_analytics.duckdb")
    res = con.execute("SELECT AVG(is_on_time) FROM fact_shipments").fetchone()[0]
    assert 0.70 <= res <= 0.95