"""
§14 Airflow DAG — DB 적재 → 마트 갱신 → 품질 검증

Local: AIRFLOW_HOME=analytics/airflow airflow dags test pivot_mvp_pipeline 2026-07-02
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "pivot-seoul",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pivot_mvp_pipeline",
    description="Pivot Seoul MVP: load → mart refresh → quality checks",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 7, 1),
    schedule="@daily",
    catchup=False,
    tags=["pivot-seoul", "mvp", "data-efficiency"],
) as dag:
    load_reference = BashOperator(
        task_id="load_reference",
        bash_command="cd /opt/pivotseoul && ./db/load.sh --reference-only",
    )

    load_demo = BashOperator(
        task_id="load_demo",
        bash_command="cd /opt/pivotseoul && ./db/load.sh --demo-only",
    )

    refresh_mart = BashOperator(
        task_id="refresh_analytics_mart",
        bash_command="cd /opt/pivotseoul && ./db/load.sh --mart-only",
    )

    run_quality = BashOperator(
        task_id="run_quality_checks",
        bash_command="cd /opt/pivotseoul && ./db/load.sh --quality",
    )

    explain_queries = BashOperator(
        task_id="explain_key_queries",
        bash_command="cd /opt/pivotseoul && ./db/load.sh --explain",
    )

    load_reference >> load_demo >> refresh_mart >> run_quality >> explain_queries
