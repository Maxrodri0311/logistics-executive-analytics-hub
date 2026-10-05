# 📦 Logistics KPI Automation & Multi-Carrier Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP_Engine-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-DAX_Semantic_Layer-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Tableau](https://img.shields.io/badge/Tableau-Hyper_Extracts-E97627?style=for-the-badge&logo=tableau&logoColor=white)](https://www.tableau.com/)
[![Excel Automation](https://img.shields.io/badge/Excel-OpenPyXL_Engine-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://openpyxl.readthedocs.io/)
[![Pytest](https://img.shields.io/badge/Pytest-100%25_Passing-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An end-to-end data analytics platform and automated reporting pipeline designed for e-commerce logistics gateways and shipping aggregators (e.g., Multi-Carrier Logistics Practice / Logistics Gateway Practice).

The platform transforms raw shipping quotes and tracking events into an optimized **Kimball Star Schema** using **DuckDB**, computes an **Enterprise DAX Semantic Layer** for Power BI/Tableau, and compiles board-ready **Executive Excel KPI Dashboards** with zero manual overhead.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    A["📦 Raw Carrier Quotes & Tracking Webhooks"] --> B["🗄️ Raw Parquet Lakehouse"]
    B --> C["⚡ DuckDB OLAP Transformation Engine"]
    C --> D["⭐ Kimball Star Schema Data Warehouse"]
    
    D --> E["📊 Power BI VertiPaq DAX Suite"]
    D --> F["📈 Tableau Hyper & Looker SQL Views"]
    D --> G["📑 Headless OpenPyXL Excel Engine"]
    
    E --> H["🚀 Interactive Executive Reports"]
    F --> I["🔍 Self-Service Multi-Dimensional BI"]
    G --> J["💼 C-Level Board-Ready Workbook (.xlsx)"]

    style A fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style B fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style C fill:#1E293B,stroke:#F59E0B,stroke-width:2px,color:#FFFFFF
    style D fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#FFFFFF
    style E fill:#1E293B,stroke:#818CF8,stroke-width:2px,color:#FFFFFF
    style F fill:#1E293B,stroke:#818CF8,stroke-width:2px,color:#FFFFFF
    style G fill:#1E293B,stroke:#818CF8,stroke-width:2px,color:#FFFFFF
    style H fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#FFFFFF
    style I fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#FFFFFF
    style J fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#FFFFFF
```

---

## 🗄️ Kimball Star Schema Topology

```mermaid
flowchart LR
    DC["dim_carriers<br/>(Carrier ID, SLAs, Contract Tiers)"] -->|carrier_id| FS["★ fact_shipments<br/>(Shipment ID, Weight, Rates, Margin, SLAs)"]
    DM["dim_merchants<br/>(Merchant ID, Tiers, Category, Markup)"] -->|merchant_id| FS
    DG["dim_geography<br/>(Geo ID, Region, Zone Type, Surcharges)"] -->|dest_geo_id| FS
    DD["dim_date<br/>(Date ID, Year, Month, Week, Day)"] -->|order_date_id| FS

    DC -->|carrier_id| FQ["★ fact_carrier_quotes<br/>(Quote ID, Rates, Transit, Conversion)"]
    DM -->|merchant_id| FQ
    DD -->|quote_date_id| FQ

    style FS fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#FFFFFF
    style FQ fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#FFFFFF
    style DC fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style DM fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style DG fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style DD fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
```

### 📋 Dimensional Data Dictionary

| Table Name | Type | Key Fields / Grain | Business Role & Cardinality |
| :--- | :---: | :--- | :--- |
| **`fact_shipments`** | Fact (Accumulating) | `shipment_id` (PK), `carrier_id` (FK), `merchant_id` (FK), `dest_geo_id` (FK), `order_date_id` (FK) | Granular shipment lifecycle: billing, carrier cost, net margin, transit time & SLA breach flags. |
| **`fact_carrier_quotes`** | Fact (Transactional) | `quote_id` (PK), `carrier_id` (FK), `merchant_id` (FK), `quote_date_id` (FK) | Real-time shipping quote requests and conversion rate to active shipments. |
| **`dim_carriers`** | Dimension (Conformed) | `carrier_id` (PK), `carrier_name`, `contract_tier`, `service_level` | Carrier master catalog with contractual SLA commitments and audit rates. |
| **`dim_merchants`** | Dimension (Conformed) | `merchant_id` (PK), `merchant_name`, `merchant_tier`, `industry_category` | E-commerce merchant catalog, volume tiers, and target markup percentages. |
| **`dim_geography`** | Dimension (Conformed) | `geo_id` (PK), `state_region`, `zone_type`, `remote_surcharge` | Logistics zones, hub classifications, and extended remote delivery surcharges. |
| **`dim_date`** | Dimension (Role-Playing) | `date_id` (PK), `full_date`, `year`, `quarter`, `month`, `week_of_year` | Date dimension supporting Time Intelligence (`MTD`, `YTD`, `MoM`, `Moving Averages`). |


---

## 📁 Repository Structure

```text
├── benchmarks/
│   └── run_benchmark.py            # Latency (p50/p95/p99) & columnar compression benchmarking
├── data/
│   ├── raw/                        # Ingested raw event datasets
│   └── processed/                  # DuckDB database (logistics_analytics.duckdb) & Star Schema
├── dist/
│   └── Executive_Logistics_KPI_Dashboard.xlsx # Automated C-Level executive workbook output
├── src/
│   ├── data_generator.py           # Synthetic e-commerce logistics event generator
│   ├── dimensional_model.py        # DuckDB Kimball Star Schema transformation & OLAP engine
│   ├── dax_measures.dax            # 25+ Enterprise DAX measures for Power BI / Analysis Services
│   ├── tableau_looker_views.sql    # Flat semantic views for Tableau Hyper & Looker Studio
│   ├── excel_builder.py            # Headless OpenPyXL executive dashboard builder with formatting
│   └── main.py                     # Master pipeline orchestrator
├── tests/
│   ├── test_core.py                # Test entrypoint
│   └── test_pipeline.py            # Pytest suite (data integrity, referential keys, financial math)
├── Dockerfile                      # Containerized deployment pipeline
├── docker-compose.yml              # Local container orchestration with volume mapping
├── pyproject.toml                  # PEP 621 packaging & test configuration
├── requirements.txt                # Production dependencies
└── README.md                       # Documentation & architecture guide
```

---

## 🎯 Key Engineering Highlights

* **Automated C-Level Reporting Pipeline:** Eliminates manual CSV extraction and spreadsheet formatting, compiling a fully-styled multi-sheet executive workbook in under 1 second.
* **In-Memory Star Schema with DuckDB:** Achieves an **83.3% storage compression ratio** (4.24 MB raw $\rightarrow$ 0.71 MB ZSTD Parquet) with **p95 analytical query latencies <15ms**.
* **Carrier Margin Leakage Auditing:** Automatically reconciles quoted merchant rates vs. billed carrier fees, highlighting volumetric re-weigh discrepancies and remote zone surcharges across carriers.
* **Multi-Platform Semantic Ready:** Features pre-computed DAX measures (Time Intelligence, Moving Averages, Pareto GMV) and flat SQL views compatible with Power BI, Tableau, and Looker Studio.

---

## 📊 Performance Benchmarks

Benchmarked on **15,000+ shipment events** across 50 iterations per query:

| Analytical Query & Dimension Slice | p50 Latency | p95 Latency | p99 Latency | Avg Throughput |
| :--- | :---: | :---: | :---: | :---: |
| **Carrier Operational Scorecard** | `12.51 ms` | `14.28 ms` | `20.85 ms` | ~80 req/sec |
| **Time Intelligence Monthly Trend** | `13.27 ms` | `15.77 ms` | `17.16 ms` | ~75 req/sec |
| **Regional Route & SLA Matrix** | `11.34 ms` | `13.62 ms` | `15.10 ms` | ~90 req/sec |

* **Storage Compression:** `4.24 MB` in-memory $\rightarrow$ **`0.71 MB` Parquet (83.3% space reduction)**.
* **Data Integrity:** **0 orphaned foreign keys (100% referential integrity)** across all Kimball dimensions.

---

## 📦 Quickstart

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/TU_USUARIO/logistics-kpi-analytics-platform.git
cd logistics-kpi-analytics-platform

python -m venv venv

# Windows:
.\venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the End-to-End Pipeline
```bash
python src/main.py --shipments 35000 --quotes 50000 --days 180
```
> Generated output will be available at: `dist/Executive_Logistics_KPI_Dashboard.xlsx`

### 3. Run Automated Tests
```bash
pytest tests/ -v --tb=short
```

### 4. Run Benchmarks
```bash
python benchmarks/run_benchmark.py
```

### 5. Run via Docker
```bash
docker-compose up --build
```

---

## 👨‍💻 Author & Contact

**Maximiliano Rodriguez**  
*Data Analytics • BI Solutions • Data Architecture*  

<br/>

[![LinkedIn Profile](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maximiliano-rodriguez-982674375/)
[![GitHub Profile](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Maxrodri0311)
[![Email Contact](https://img.shields.io/badge/Gmail-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:maxrodri0311@gmail.com)

<br/>

* 💼 **LinkedIn:** [maximiliano-rodriguez-982674375](https://www.linkedin.com/in/maximiliano-rodriguez-982674375/)
* 🐙 **GitHub:** [Maxrodri0311](https://github.com/Maxrodri0311)
* 📧 **Email:** `maxrodri0311@gmail.com`