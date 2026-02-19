"""Supabase HTTP API client utility."""
import os
import httpx
from typing import Optional, List, Dict, Any
from src.utils.logger import get_logger


class SupabaseClient:
    """Supabase REST API client for database operations."""
    
    _instance: Optional['SupabaseClient'] = None
    _logger = get_logger(__name__)
    
    def __init__(self):
        """Initialize the Supabase client."""
        self.project_url = os.getenv("SUPABASE_URL", "https://qntmzwnuocjfyjigsywu.supabase.co")
        self.api_key = os.getenv("SUPABASE_KEY", "")
        self.rest_url = f"{self.project_url}/rest/v1"
        
        if not self.api_key:
            self._logger.warning("SUPABASE_KEY not set - API calls will fail")
        
        self._logger.info(f"SupabaseClient initialized with URL: {self.project_url}")
    
    @classmethod
    def get_instance(cls) -> 'SupabaseClient':
        """Get singleton instance of SupabaseClient."""
        if cls._instance is None:
            cls._instance = SupabaseClient()
        return cls._instance
    
    def _get_headers(self, prefer: str = "return=representation") -> Dict[str, str]:
        """
        Get headers for Supabase API requests.
        
        Args:
            prefer: Prefer header value for response format
        
        Returns:
            Dictionary of headers
        """
        return {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": prefer
        }
    
    async def select(
        self, 
        table: str, 
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Select records from a table.
        
        Args:
            table: Table name
            columns: Columns to select (default "*")
            filters: Dictionary of filters {column: value} or {column: "operator.value"}
            order: Order by column (e.g., "name.asc" or "created_at.desc")
            limit: Maximum number of records to return
        
        Returns:
            List of records as dictionaries
        """
        self._logger.debug(f"SELECT from {table}, columns={columns}, filters={filters}")
        
        url = f"{self.rest_url}/{table}?select={columns}"
        
        # Add filters
        if filters:
            for column, value in filters.items():
                if value is None or value == "is.null":
                    url += f"&{column}=is.null"
                elif isinstance(value, list):
                    in_val = "in.(" + ",".join(str(v) for v in value) + ")"
                    url += f"&{column}={in_val}"
                elif isinstance(value, str) and any(op in value for op in ['eq.', 'neq.', 'gt.', 'gte.', 'lt.', 'lte.', 'like.', 'ilike.', 'in.']):
                    url += f"&{column}={value}"
                else:
                    url += f"&{column}=eq.{value}"
        
        # Add order
        if order:
            url += f"&order={order}"
        
        # Add limit
        if limit:
            url += f"&limit={limit}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self._get_headers())
                response.raise_for_status()
                
                result = response.json()
                self._logger.debug(f"SELECT returned {len(result)} records")
                return result
                
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error in SELECT: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self._logger.error(f"Error in SELECT: {e}", exc_info=True)
            raise
    
    async def insert(
        self, 
        table: str, 
        data: Dict[str, Any],
        return_data: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Insert a record into a table.
        
        Args:
            table: Table name
            data: Dictionary of column values
            return_data: Whether to return the inserted record
        
        Returns:
            Inserted record if return_data is True, else None
        """
        self._logger.debug(f"INSERT into {table}")
        # Omit null values so PostgREST/DB use column defaults (avoids 409 in some setups)
        payload = {k: v for k, v in data.items() if v is not None}
        url = f"{self.rest_url}/{table}"
        prefer = "return=representation" if return_data else "return=minimal"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, 
                    headers=self._get_headers(prefer),
                    json=payload
                )
                response.raise_for_status()
                
                if return_data:
                    result = response.json()
                    self._logger.debug(f"INSERT successful, returned record")
                    return result[0] if result else None
                
                self._logger.debug("INSERT successful")
                return None
                
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error in INSERT: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self._logger.error(f"Error in INSERT: {e}", exc_info=True)
            raise
    
    async def update(
        self, 
        table: str, 
        data: Dict[str, Any],
        filters: Dict[str, Any],
        return_data: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Update records in a table.
        
        Args:
            table: Table name
            data: Dictionary of column values to update
            filters: Dictionary of filters to identify records
            return_data: Whether to return updated records
        
        Returns:
            Updated records if return_data is True, else None
        """
        self._logger.debug(f"UPDATE {table} with filters={filters}")
        
        url = f"{self.rest_url}/{table}"
        
        # Add filters
        filter_parts = []
        for column, value in filters.items():
            if value is None or value == "is.null":
                filter_parts.append(f"{column}=is.null")
            elif isinstance(value, str) and any(op in value for op in ['eq.', 'neq.', 'gt.', 'gte.', 'lt.', 'lte.']):
                filter_parts.append(f"{column}={value}")
            else:
                filter_parts.append(f"{column}=eq.{value}")
        
        if filter_parts:
            url += "?" + "&".join(filter_parts)
        
        prefer = "return=representation" if return_data else "return=minimal"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    url, 
                    headers=self._get_headers(prefer),
                    json=data
                )
                response.raise_for_status()
                
                if return_data:
                    result = response.json()
                    self._logger.debug(f"UPDATE successful, {len(result)} records updated")
                    return result
                
                self._logger.debug("UPDATE successful")
                return None
                
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error in UPDATE: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self._logger.error(f"Error in UPDATE: {e}", exc_info=True)
            raise
    
    async def delete(
        self, 
        table: str, 
        filters: Dict[str, Any],
        return_data: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Delete records from a table.
        
        Args:
            table: Table name
            filters: Dictionary of filters to identify records
            return_data: Whether to return deleted records
        
        Returns:
            Deleted records if return_data is True, else None
        """
        self._logger.debug(f"DELETE from {table} with filters={filters}")
        
        url = f"{self.rest_url}/{table}"
        
        # Add filters (required for DELETE)
        filter_parts = []
        for column, value in filters.items():
            if value is None or value == "is.null":
                filter_parts.append(f"{column}=is.null")
            elif isinstance(value, str) and any(op in value for op in ['eq.', 'neq.', 'gt.', 'gte.', 'lt.', 'lte.']):
                filter_parts.append(f"{column}={value}")
            else:
                filter_parts.append(f"{column}=eq.{value}")
        
        if filter_parts:
            url += "?" + "&".join(filter_parts)
        
        prefer = "return=representation" if return_data else "return=minimal"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=self._get_headers(prefer))
                response.raise_for_status()
                
                if return_data:
                    result = response.json()
                    self._logger.debug(f"DELETE successful, {len(result)} records deleted")
                    return result
                
                self._logger.debug("DELETE successful")
                return None
                
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error in DELETE: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self._logger.error(f"Error in DELETE: {e}", exc_info=True)
            raise
    
    async def rpc(
        self, 
        function_name: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call a PostgreSQL function via RPC.
        Use this for complex queries (JOINs, CTEs, aggregations).
        
        Args:
            function_name: Name of the PostgreSQL function
            params: Dictionary of function parameters
        
        Returns:
            Function result (type depends on function)
        """
        self._logger.debug(f"RPC call to {function_name} with params={params}")
        
        url = f"{self.rest_url}/rpc/{function_name}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=params or {}
                )
                response.raise_for_status()
                
                result = response.json()
                self._logger.debug(f"RPC {function_name} returned successfully")
                return result
                
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error in RPC {function_name}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self._logger.error(f"Error in RPC {function_name}: {e}", exc_info=True)
            raise
    
    async def raw_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query via a generic RPC function.
        Requires a 'execute_sql' function to be created in the database.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Query results as list of dictionaries
        """
        self._logger.debug(f"Executing raw query")
        return await self.rpc("execute_sql", {"query": query, "params": params or {}})

