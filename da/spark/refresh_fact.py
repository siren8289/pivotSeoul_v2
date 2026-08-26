"""
§12 Spark 분산 집계 — analytics.fact_simulation_run 증분 갱신 (선택 실행)

Requires: pyspark, PostgreSQL JDBC driver on Spark classpath.

  spark-submit \
    --packages org.postgresql:postgresql:42.7.3 \
    da/spark/refresh_fact.py \
    --jdbc-url jdbc:postgresql://localhost:5432/pivotseoul \
    --db-user pivotseoul \
    --db-password pivotseoul
"""

from __future__ import annotations

import argparse
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh Pivot Seoul analytics fact via Spark")
    parser.add_argument("--jdbc-url", required=True)
    parser.add_argument("--db-user", required=True)
    parser.add_argument("--db-password", required=True)
    parser.add_argument("--watermark", default="1970-01-01 00:00:00")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    spark = (
        SparkSession.builder.appName("pivot-mvp-fact-refresh")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .getOrCreate()
    )

    jdbc_props = {
        "user": args.db_user,
        "password": args.db_password,
        "driver": "org.postgresql.Driver",
    }

    runs = (
        spark.read.jdbc(args.jdbc_url, "simulation_run", properties=jdbc_props)
        .filter(F.col("run_status") == "COMPLETED")
        .filter(F.coalesce(F.col("updated_at"), F.col("completed_at")) > F.lit(args.watermark))
        .cache()
    )

    sessions = spark.read.jdbc(args.jdbc_url, "simulation_session", properties=jdbc_props)
    life_stages = spark.read.jdbc(args.jdbc_url, "life_stage", properties=jdbc_props)
    conditions = spark.read.jdbc(args.jdbc_url, "user_condition", properties=jdbc_props)
    results = spark.read.jdbc(args.jdbc_url, "scenario_result", properties=jdbc_props)
    thresholds = spark.read.jdbc(args.jdbc_url, "threshold_result", properties=jdbc_props)

    fact = (
        runs.alias("r")
        .join(sessions.alias("s"), "session_id")
        .join(life_stages.alias("ls"), sessions.life_stage_id == life_stages.life_stage_id)
        .join(conditions.alias("uc"), "session_id", "left")
        .join(results.alias("sr"), results.simulation_run_id == runs.simulation_run_id, "left")
        .join(thresholds.alias("tr"), thresholds.scenario_result_id == results.scenario_result_id, "left")
        .select(
            runs.simulation_run_id.alias("simulation_run_id"),
            runs.session_id.alias("session_id"),
            results.scenario_result_id.alias("scenario_result_id"),
            sessions.life_stage_id.alias("life_stage_id"),
            life_stages.stage_code.alias("life_stage_code"),
            conditions.current_district.alias("current_district"),
            F.date_format(F.coalesce(runs.completed_at, runs.started_at), "yyyyMMdd").cast("int").alias("run_date_id"),
            thresholds.calculated_value.alias("rir_value"),
            F.coalesce(thresholds.is_red_zone, F.lit(False)).alias("is_red_zone"),
            results.risk_score.alias("risk_score"),
            runs.run_status.alias("run_status"),
            F.lit(datetime.utcnow()).alias("refreshed_at"),
        )
        .dropDuplicates(["simulation_run_id"])
    )

    row_count = fact.count()
    print(f"Prepared {row_count} fact rows")

    if row_count > 0:
        fact.write.jdbc(
            args.jdbc_url,
            "analytics.fact_simulation_run",
            mode="append",
            properties=jdbc_props,
        )

    spark.stop()


if __name__ == "__main__":
    main()
