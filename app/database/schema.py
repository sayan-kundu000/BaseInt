"""Database schema reflection utilities using SQLAlchemy."""

from sqlalchemy import inspect
from typing import Dict, Any, List


def inspect_database_schema(engine) -> Dict[str, Any]:
    """Extract full table schema, column definitions, types, and primary keys via SQLAlchemy reflection."""
    inspector = inspect(engine)
    schema_info: Dict[str, Any] = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)

        col_defs = []
        for col in columns:
            col_type = str(col.get("type", "UNKNOWN"))
            is_pk = col.get("name") in (pk_constraint.get("constrained_columns") or [])
            nullable = col.get("nullable", True)
            col_defs.append({
                "name": col["name"],
                "type": col_type,
                "primary_key": is_pk,
                "nullable": nullable
            })

        schema_info[table_name] = {
            "columns": col_defs,
            "primary_key": pk_constraint.get("constrained_columns", []),
            "foreign_keys": [
                {
                    "constrained_columns": fk.get("constrained_columns", []),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns", [])
                }
                for fk in foreign_keys
            ]
        }

    return schema_info


def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """Format dictionary schema metadata into an expressive prompt string for LLM generation."""
    lines = ["Available Database Tables and Schema Definitions:"]
    for table_name, meta in schema_info.items():
        lines.append(f"\nTable: {table_name}")
        for col in meta["columns"]:
            pk_tag = " [PRIMARY KEY]" if col["primary_key"] else ""
            lines.append(f"  - {col['name']} ({col['type']}){pk_tag}")
        if meta.get("foreign_keys"):
            for fk in meta["foreign_keys"]:
                lines.append(
                    f"  * FOREIGN KEY ({', '.join(fk['constrained_columns'])}) "
                    f"REFERENCES {fk['referred_table']}({', '.join(fk['referred_columns'])})"
                )
    return "\n".join(lines)
