#!/usr/bin/env python3
"""
Complete Synthea-to-PostgreSQL workflow with LLM integration.
This script demonstrates the full pipeline from Synthea CSV files to OMOP analytics.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class SyntheaWorkflow:
    def __init__(self, mcp_client):
        self.client = mcp_client
        self.sandbox_id = None

    async def setup_environment(self) -> bool:
        """Set up the sandbox environment with required packages."""
        try:
            # Create sandbox
            print("🔧 Creating sandbox...")
            resp = await self.client.call_tool("create_sandbox", {})
            if not resp.get("success"):
                raise Exception(f"Failed to create sandbox: {resp}")

            self.sandbox_id = resp["sandbox_id"]
            print(f"✅ Sandbox created: {self.sandbox_id}")

            # Install required packages
            print("📦 Installing packages...")
            packages = ["pandas", "psycopg2-binary", "sqlalchemy"]
            for package in packages:
                resp = await self.client.call_tool(
                    "install_package",
                    {"sandbox_id": self.sandbox_id, "package": package},
                )
                print(f"✅ Installed {package}")

            return True

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

    async def create_omop_schema(self) -> bool:
        """Create OMOP CDM schema in PostgreSQL."""
        try:
            print("🏗️ Creating OMOP schema...")
            resp = await self.client.call_tool(
                "create_omop_schema", {"sandbox_id": self.sandbox_id}
            )

            if resp.get("exit_code") == 0:
                print("✅ OMOP schema created")
                return True
            else:
                print(f"❌ Schema creation failed: {resp.get('output')}")
                return False

        except Exception as e:
            print(f"❌ Schema creation error: {e}")
            return False

    async def load_synthea_data(self) -> bool:
        """Load Synthea CSV files into PostgreSQL."""
        try:
            print("📊 Loading Synthea data...")
            resp = await self.client.call_tool(
                "load_synthea_to_postgres",
                {"sandbox_id": self.sandbox_id, "csv_directory": "/synthetic_data"},
            )

            if resp.get("exit_code") == 0:
                print("✅ Synthea data loaded")
                return True
            else:
                print(f"❌ Data loading failed: {resp.get('output')}")
                return False

        except Exception as e:
            print(f"❌ Data loading error: {e}")
            return False

    async def run_analytics(self) -> Dict[str, Any]:
        """Run various analytics on the OMOP data."""
        results = {}

        try:
            print("📈 Running analytics...")

            # Basic counts
            resp = await self.client.call_tool(
                "analyze_omop_data",
                {"sandbox_id": self.sandbox_id, "analysis_type": "basic"},
            )

            if resp.get("exit_code") == 0:
                results["basic_counts"] = json.loads(resp.get("output", "{}"))
                print("✅ Basic analytics completed")

            # Demographics
            resp = await self.client.call_tool(
                "analyze_omop_data",
                {"sandbox_id": self.sandbox_id, "analysis_type": "demographics"},
            )

            if resp.get("exit_code") == 0:
                results["demographics"] = json.loads(resp.get("output", "[]"))
                print("✅ Demographics analysis completed")

            # LLM-friendly operations
            llm_operations = [
                "Count total patients",
                "Show age distribution",
                "Count unique conditions",
                "Show gender distribution",
            ]

            results["llm_operations"] = {}
            for operation in llm_operations:
                resp = await self.client.call_tool(
                    "llm_dataframe_operation",
                    {"sandbox_id": self.sandbox_id, "operation": operation},
                )

                if resp.get("exit_code") == 0:
                    results["llm_operations"][operation] = json.loads(
                        resp.get("output", "{}")
                    )

            print("✅ All analytics completed")
            return results

        except Exception as e:
            print(f"❌ Analytics error: {e}")
            return {"error": str(e)}

    async def cleanup(self):
        """Clean up the sandbox."""
        if self.sandbox_id:
            try:
                await self.client.call_tool(
                    "remove_sandbox", {"sandbox_id": self.sandbox_id, "force": True}
                )
                print("🧹 Sandbox cleaned up")
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")


async def main():
    """Main workflow execution."""
    print("🚀 Synthea-to-PostgreSQL Workflow")
    print("=" * 50)

    # Note: This would need to be adapted for your MCP client
    # For now, this shows the workflow structure
    workflow = SyntheaWorkflow(None)  # Replace with actual MCP client

    try:
        # Setup
        if not await workflow.setup_environment():
            return

        # Create schema
        if not await workflow.create_omop_schema():
            return

        # Load data
        if not await workflow.load_synthea_data():
            return

        # Run analytics
        results = await workflow.run_analytics()

        # Display results
        print("\n📊 Results Summary:")
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"❌ Workflow failed: {e}")

    finally:
        await workflow.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
