"""
LumenOps 360 — Load CSVs to DuckDB
Reads all generated CSVs from data/raw/ and loads them into
data/lumenops.duckdb under a 'raw' schema.

Uses read_csv_auto to preserve original CSV column headers —
no rigid DDL that can mismatch the generator output.

Usage:
    cd LumenOps-360
    python src/load_to_duckdb.py
"""

import duckdb
import pathlib
import sys

# ── Paths ────────────────────────────────────────────────────
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "lumenops.duckdb"

# Expected tables (just filenames, no DDL — schema comes from CSV headers)
EXPECTED_TABLES = [
    "dim_date",
    "dim_customer",
    "dim_product",
    "dim_line",
    "dim_shift",
    "dim_defect_reason",
    "dim_downtime_reason",
    "dim_supplier",
    "fact_production_log",
    "fact_qc_inspection",
    "fact_sales_orders",
    "fact_material_requisitions",
    "fact_dispatch",
    "fact_supplier_delivery",
]


def main():
    print("=" * 60)
    print("  LumenOps 360 — DuckDB Loader")
    print(f"  Source:  {RAW_DIR}")
    print(f"  Target:  {DB_PATH}")
    print("=" * 60)

    # Verify CSVs exist
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        print(f"\n  ❌ No CSV files found in {RAW_DIR}")
        print("  Run 'python src/generate_data.py' first.")
        sys.exit(1)

    print(f"\n▸ Found {len(csv_files)} CSV files")

    # Remove old DB if present (clean load every time)
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("  Removed existing lumenops.duckdb (clean load)")

    # Connect and create raw schema
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # Load each table — auto-detect schema from CSV headers
    loaded = 0
    total_rows = 0

    for table_name in EXPECTED_TABLES:
        csv_path = RAW_DIR / f"{table_name}.csv"
        if not csv_path.exists():
            print(f"  ⚠  {table_name}.csv not found — skipping")
            continue

        # Create table directly from CSV (preserves headers as column names)
        con.execute(f"""
            CREATE TABLE raw.{table_name} AS
            SELECT * FROM read_csv_auto('{csv_path}',
                header=true,
                dateformat='%Y-%m-%d'
            )
        """)

        row_count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
        col_names = [r[0] for r in con.execute(f"DESCRIBE raw.{table_name}").fetchall()]
        total_rows += row_count
        loaded += 1
        print(f"  ✓ raw.{table_name}: {row_count:,} rows  [{', '.join(col_names)}]")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  LOAD COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Tables loaded: {loaded}")
    print(f"  Total rows:    {total_rows:,}")
    print(f"  Database:      {DB_PATH}")

    # Quick integrity checks
    print(f"\n▸ Integrity checks...")

    orphan_skus = con.execute("""
        SELECT COUNT(DISTINCT pl.sku)
        FROM raw.fact_production_log pl
        LEFT JOIN raw.dim_product dp ON pl.sku = dp.sku
        WHERE dp.sku IS NULL
    """).fetchone()[0]
    print(f"  Production log orphan SKUs:    {orphan_skus}  {'✓' if orphan_skus == 0 else '❌'}")

    orphan_cust = con.execute("""
        SELECT COUNT(DISTINCT so.customer_id)
        FROM raw.fact_sales_orders so
        LEFT JOIN raw.dim_customer dc ON so.customer_id = dc.customer_id
        WHERE dc.customer_id IS NULL
    """).fetchone()[0]
    print(f"  Sales order orphan customers:  {orphan_cust}  {'✓' if orphan_cust == 0 else '❌'}")

    orphan_disp = con.execute("""
        SELECT COUNT(DISTINCT d.order_id)
        FROM raw.fact_dispatch d
        LEFT JOIN raw.fact_sales_orders so ON d.order_id = so.order_id
        WHERE so.order_id IS NULL
    """).fetchone()[0]
    print(f"  Dispatch orphan orders:        {orphan_disp}  {'✓' if orphan_disp == 0 else '❌'}")

    date_range = con.execute("""
        SELECT MIN(date), MAX(date) FROM raw.fact_production_log
    """).fetchone()
    print(f"  Production date range:         {date_range[0]} → {date_range[1]}  ✓")

    print(f"\n  ✅ DuckDB ready. Next step: cd lumenops && dbt run --profiles-dir .")

    con.close()


if __name__ == "__main__":
    main()
