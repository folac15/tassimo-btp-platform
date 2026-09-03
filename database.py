import os
from typing import Optional, Dict, Any, List

from supabase import create_client, Client


# ============================================================
# TASSIMO BTP CONSTRUCTION SARL
# DATABASE CONNECTION LAYER
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class Database:
    """
    Central database service for the TASSIMO platform.

    All modules should eventually communicate with Supabase
    through this class rather than creating separate database
    connections throughout the application.
    """

    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.client: Optional[Client] = None

        if self.url and self.key:
            try:
                self.client = create_client(
                    self.url,
                    self.key
                )
            except Exception as error:
                print(f"[DATABASE] Connection initialization failed: {error}")

    # ========================================================
    # CONNECTION STATUS
    # ========================================================

    def is_configured(self) -> bool:
        """Check whether Supabase credentials are configured."""

        return bool(
            self.url and
            self.key and
            self.client
        )

    # ========================================================
    # GENERIC SELECT
    # ========================================================

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve records from a Supabase table.
        """

        if not self.is_configured():
            return []

        try:
            query = self.client.table(table).select(columns)

            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            if order_by:
                query = query.order(
                    order_by,
                    desc=descending
                )

            if limit:
                query = query.limit(limit)

            response = query.execute()

            return response.data or []

        except Exception as error:
            print(
                f"[DATABASE] SELECT error on {table}: {error}"
            )
            return []

    # ========================================================
    # GET ONE RECORD
    # ========================================================

    def get_one(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve one record matching the supplied filters.
        """

        records = self.select(
            table=table,
            filters=filters,
            limit=1
        )

        if records:
            return records[0]

        return None

    # ========================================================
    # INSERT
    # ========================================================

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Insert one record.
        """

        if not self.is_configured():
            return None

        try:
            response = (
                self.client
                .table(table)
                .insert(data)
                .execute()
            )

            if response.data:
                return response.data[0]

            return None

        except Exception as error:
            print(
                f"[DATABASE] INSERT error on {table}: {error}"
            )
            return None

    # ========================================================
    # INSERT MANY
    # ========================================================

    def insert_many(
        self,
        table: str,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Insert multiple records.
        """

        if not self.is_configured() or not data:
            return []

        try:
            response = (
                self.client
                .table(table)
                .insert(data)
                .execute()
            )

            return response.data or []

        except Exception as error:
            print(
                f"[DATABASE] BULK INSERT error on {table}: {error}"
            )
            return []

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update records matching the supplied filters.
        """

        if not self.is_configured():
            return None

        try:
            query = self.client.table(table).update(data)

            for column, value in filters.items():
                query = query.eq(column, value)

            response = query.execute()

            if response.data:
                return response.data[0]

            return None

        except Exception as error:
            print(
                f"[DATABASE] UPDATE error on {table}: {error}"
            )
            return None

    # ========================================================
    # UPSERT
    # ========================================================

    def upsert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Insert a record or update it when a matching unique
        record already exists.
        """

        if not self.is_configured():
            return None

        try:
            response = (
                self.client
                .table(table)
                .upsert(data)
                .execute()
            )

            if response.data:
                return response.data[0]

            return None

        except Exception as error:
            print(
                f"[DATABASE] UPSERT error on {table}: {error}"
            )
            return None

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> bool:
        """
        Delete records matching the supplied filters.
        """

        if not self.is_configured():
            return False

        try:
            query = self.client.table(table).delete()

            for column, value in filters.items():
                query = query.eq(column, value)

            query.execute()

            return True

        except Exception as error:
            print(
                f"[DATABASE] DELETE error on {table}: {error}"
            )
            return False

    # ========================================================
    # COMPANY PROFILE
    # ========================================================

    def get_company_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get the TASSIMO company profile.
        """

        return self.get_one(
            "company_profile",
            {}
        )

    # ========================================================
    # CUSTOMERS
    # ========================================================

    def get_customers(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get customers/prospects.
        """

        return self.select(
            table="customers",
            limit=limit,
            order_by="created_at",
            descending=True
        )

    def get_customer(
        self,
        customer_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get one customer by ID.
        """

        return self.get_one(
            "customers",
            {"id": customer_id}
        )

    def create_customer(
        self,
        customer_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a customer/prospect.
        """

        return self.insert(
            "customers",
            customer_data
        )

    def update_customer(
        self,
        customer_id: str,
        customer_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a customer/prospect.
        """

        return self.update(
            "customers",
            {"id": customer_id},
            customer_data
        )

    # ========================================================
    # PROJECTS
    # ========================================================

    def get_projects(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get construction projects.
        """

        return self.select(
            table="projects",
            limit=limit,
            order_by="created_at",
            descending=True
        )

    def get_project(
        self,
        project_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get one project.
        """

        return self.get_one(
            "projects",
            {"id": project_id}
        )

    # ========================================================
    # PAYMENTS
    # ========================================================

    def get_payments(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get business payments.
        """

        return self.select(
            table="payments",
            limit=limit,
            order_by="created_at",
            descending=True
        )

    # ========================================================
    # COURSES
    # ========================================================

    def get_courses(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get training courses.
        """

        return self.select(
            table="courses",
            limit=limit,
            order_by="created_at",
            descending=True
        )

    # ========================================================
    # DASHBOARD STATISTICS
    # ========================================================

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get basic statistics for the CEO dashboard.
        """

        if not self.is_configured():
            return {
                "database_connected": False,
                "customers": 0,
                "projects": 0,
                "payments": 0,
                "courses": 0
            }

        try:
            customers = self.select(
                "customers",
                columns="id"
            )

            projects = self.select(
                "projects",
                columns="id"
            )

            payments = self.select(
                "payments",
                columns="id"
            )

            courses = self.select(
                "courses",
                columns="id"
            )

            return {
                "database_connected": True,
                "customers": len(customers),
                "projects": len(projects),
                "payments": len(payments),
                "courses": len(courses)
            }

        except Exception as error:
            print(
                f"[DATABASE] Dashboard statistics error: {error}"
            )

            return {
                "database_connected": False,
                "customers": 0,
                "projects": 0,
                "payments": 0,
                "courses": 0
            }


# ============================================================
# SINGLE DATABASE INSTANCE
# ============================================================

db = Database()
