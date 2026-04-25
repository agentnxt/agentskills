"""Data Analysis skill for CrewAI agents."""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class SQLQueryInput(BaseModel):
    query: str = Field(description="SQL query to execute")
    database_url: str = Field(default="", description="Database URL (uses DATABASE_URL env if empty)")


class DataAnalysisTool(BaseTool):
    name: str = "data_analysis"
    description: str = "Execute SQL queries against a database and return results as formatted tables."
    args_schema: Type[BaseModel] = SQLQueryInput

    def _run(self, query: str, database_url: str = "") -> str:
        import os
        db_url = database_url or os.environ.get("DATABASE_URL", "")
        if not db_url:
            return "Error: No database URL provided. Set DATABASE_URL env var or pass database_url."

        try:
            import sqlalchemy
            engine = sqlalchemy.create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text(query))
                rows = result.fetchall()
                columns = result.keys()

                if not rows:
                    return "Query returned no results."

                header = " | ".join(columns)
                separator = " | ".join("---" for _ in columns)
                body = "\n".join(
                    " | ".join(str(val) for val in row) for row in rows[:100]
                )
                return f"{header}\n{separator}\n{body}"
        except Exception as e:
            return f"Error executing query: {e}"
