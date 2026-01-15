"""PostgreSQL connection utility."""
import os
import urllib.parse
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional
from src.utils.logger import get_logger
from config import config

class PostgresConnection:
	"""PostgreSQL connection pool manager."""
	
	_connection_pool: Optional[pool.ThreadedConnectionPool] = None
	_logger = get_logger(__name__)
	
	@classmethod
	def initialize_pool(cls):
		"""Initialize PostgreSQL connection pool."""
		cls._logger.debug("Initializing PostgreSQL connection pool")
		
		try:
			connection_string = cls._build_connection_string()
			
			# Log connection info without password
			safe_log = connection_string
			# Hide password in logs for both formats
			if "password=" in safe_log:
				# Format: host=... password=...
				parts = safe_log.split("password=")
				if len(parts) > 1:
					password_part = parts[1].split()[0] if " " in parts[1] else parts[1]
					safe_log = safe_log.replace(f"password={password_part}", "password=***")
			elif "://" in safe_log and "@" in safe_log:
				# Format: postgresql://user:password@host
				try:
					protocol_part = safe_log.split("://")[0] + "://"
					rest = safe_log.split("://")[1]
					if "@" in rest:
						user_pass = rest.split("@")[0]
						host_part = rest.split("@")[1]
						if ":" in user_pass:
							user = user_pass.split(":")[0]
							safe_log = f"{protocol_part}{user}:***@{host_part}"
				except:
					pass  # If parsing fails, just log as is
			cls._logger.debug(f"PostgreSQL connection string: {safe_log}")
			
			cls._connection_pool = pool.ThreadedConnectionPool(
				minconn=1,
				maxconn=10,
				dsn=connection_string,
				cursor_factory=RealDictCursor
			)
			
			cls._logger.info("PostgreSQL connection pool initialized successfully")
			
		except psycopg2.ProgrammingError as e:
			if "invalid percent-encoded token" in str(e) or "invalid dsn" in str(e).lower():
				cls._logger.error(f"PostgreSQL connection string error: {e}")
				cls._logger.error("This usually means the password contains special characters that need URL encoding.")
				cls._logger.error("The code should handle this automatically, but if the error persists:")
				cls._logger.error("1. Make sure your DATABASE_URL password is properly URL-encoded")
				cls._logger.error("2. Or use individual POSTGRES_* environment variables instead")
				cls._logger.error("3. Special characters in passwords should be encoded (e.g., @ becomes %40)")
			else:
				cls._logger.error(f"PostgreSQL programming error: {e}", exc_info=True)
			raise
		except psycopg2.OperationalError as e:
			cls._logger.error(f"PostgreSQL connection error: {e}")
			cls._logger.error("Please check your PostgreSQL connection settings:")
			cls._logger.error(f"  Host: {config.POSTGRES_HOST}")
			cls._logger.error(f"  Port: {config.POSTGRES_PORT}")
			cls._logger.error(f"  Database: {config.POSTGRES_DB}")
			cls._logger.error(f"  User: {config.POSTGRES_USER}")
			cls._logger.error("  Password: ***")
			raise
		except Exception as e:
			cls._logger.error(f"Error initializing PostgreSQL connection pool: {e}", exc_info=True)
			raise
	
	@classmethod
	def _build_connection_string(cls) -> str:
		"""Build PostgreSQL connection string from config."""
		# Check if DATABASE_URL is set (common for Supabase/cloud providers)
		database_url = os.getenv("DATABASE_URL")
		if database_url and database_url.startswith("postgresql://"):
			cls._logger.debug("Using DATABASE_URL connection string")
			
			# Always manually extract and re-encode password to handle special characters
			# This avoids issues with urlparse when password contains invalid % sequences
			try:
				# Manual extraction: postgresql://user:password@host:port/db
				if "://" in database_url and "@" in database_url:
					parts = database_url.split("://", 1)
					scheme = parts[0]
					rest = parts[1]
					
					if "@" in rest:
						auth_host = rest.split("@", 1)
						auth = auth_host[0]
						host_db = auth_host[1]
						
						if ":" in auth:
							user_pass = auth.split(":", 1)
							user = user_pass[0]
							password = user_pass[1]
							
							# Handle password encoding carefully
							# If password contains invalid % sequences (like %ue), we need to encode it
							decoded_password = password
							
							# Try to safely decode - if it contains invalid % sequences, use as-is
							try:
								# Try decoding with strict error handling
								test_decode = urllib.parse.unquote(password, errors='strict')
								# If decode worked, check if password was already encoded
								# by seeing if re-encoding matches original
								test_reencode = urllib.parse.quote(test_decode, safe="")
								if test_reencode == password:
									# Password was already properly encoded, use decoded version
									decoded_password = test_decode
								# Otherwise, password contains raw % chars, use as-is
							except (ValueError, UnicodeDecodeError, KeyError):
								# Password contains invalid percent sequences (like %ue)
								# This means it's a raw password with % characters
								# Use password as-is - we'll encode it below
								decoded_password = password
							
							# Always encode the password to ensure all special chars are encoded
							# This will turn % into %25, # into %23, ^ into %5E, etc.
							encoded_password = urllib.parse.quote(decoded_password, safe="")
							encoded_auth = f"{user}:{encoded_password}"
							database_url = f"{scheme}://{encoded_auth}@{host_db}"
							cls._logger.debug("URL-encoded password in connection string")
			except Exception as e:
				cls._logger.warning(f"Could not parse/encode DATABASE_URL, using as-is: {e}")
			
			# For Supabase, ensure SSL is required
			if "supabase.co" in database_url or "supabase.com" in database_url:
				# Add sslmode=require if not already present
				if "sslmode=" not in database_url:
					separator = "&" if "?" in database_url else "?"
					database_url = f"{database_url}{separator}sslmode=require"
					cls._logger.debug("Added SSL mode for Supabase connection")
			
			return database_url
		
		# Build connection string from individual parameters
		host = config.POSTGRES_HOST
		port = config.POSTGRES_PORT
		database = config.POSTGRES_DB
		user = config.POSTGRES_USER
		password = config.POSTGRES_PASSWORD
		
		# Validate required parameters
		if not all([host, database, user, password]):
			raise ValueError("Missing required PostgreSQL connection parameters")
		
		# Build connection string
		connection_string = f"host={host} port={port} dbname={database} user={user} password={password}"
		
		# For Supabase (pooler or direct), add SSL requirement
		if "supabase.com" in host or "supabase.co" in host or "pooler.supabase.com" in host:
			connection_string += " sslmode=require"
			cls._logger.debug("Added SSL mode for Supabase connection")
		
		return connection_string
	
	@classmethod
	def get_connection(cls):
		"""Get a connection from the pool."""
		cls._logger.debug("Getting connection from pool")
		
		if cls._connection_pool is None:
			cls.initialize_pool()
		
		try:
			connection = cls._connection_pool.getconn()
			cls._logger.debug("Connection retrieved from pool")
			return connection
			
		except Exception as e:
			cls._logger.error(f"Error getting connection from pool: {e}", exc_info=True)
			raise
	
	@classmethod
	def return_connection(cls, connection):
		"""Return a connection to the pool."""
		cls._logger.debug("Returning connection to pool")
		
		try:
			if cls._connection_pool:
				cls._connection_pool.putconn(connection)
				cls._logger.debug("Connection returned to pool")
		except Exception as e:
			cls._logger.error(f"Error returning connection to pool: {e}", exc_info=True)
	
	@classmethod
	def close_all_connections(cls):
		"""Close all connections in the pool."""
		cls._logger.debug("Closing all connections in pool")
		
		try:
			if cls._connection_pool:
				cls._connection_pool.closeall()
				cls._logger.info("All PostgreSQL connections closed")
		except Exception as e:
			cls._logger.error(f"Error closing connections: {e}", exc_info=True)

