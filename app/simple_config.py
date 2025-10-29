"""
Simple environment configuration for Render deployment
This bypasses the complex configuration system to ensure we get the right database URL
"""
import os
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Get the database URL with multiple fallback options"""
    
    # Try to get from environment variable first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.info("Using DATABASE_URL from environment variable")
        return database_url
    
    # Check if we're in production environment
    env_state = os.getenv("ENV_STATE", "dev").lower()
    if env_state == "prod":
        # Use the known Render database URL
        render_db_url = "postgresql://my_fit_user:k6lYoyTLP0UMvj1IxNWBHsbDEPQCGoMI@dpg-d40j2codl3ps73br0ka0-a/my_fit_db_x5hl"
        logger.info("Using hardcoded Render database URL for production")
        return render_db_url
    
    # Default for development
    dev_db_url = "postgresql://user:pass@localhost:5432/db"
    logger.info("Using development database URL")
    return dev_db_url

def get_secret_key():
    """Get the secret key for JWT"""
    return os.getenv("SECRET_KEY", "wJjyDWRKmfnr6UzoD_VTOVmZwzlVujMK2ZvsWiljWgA")