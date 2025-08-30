import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SecurityConfig:
    """Security configuration and validation"""
    
    # Required environment variables
    REQUIRED_VARS = [
        'BHIV_SECRET_KEY',
        'BHIV_JWT_SECRET',
        'BHIV_PASSWORD_SALT'
    ]
    
    @classmethod
    def validate_environment(cls) -> bool:
        """Validate that all required environment variables are set"""
        missing_vars = []
        
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file")
            return False
        
        return True
    
    @classmethod
    def get_config(cls) -> dict:
        """Get validated configuration"""
        if not cls.validate_environment():
            # Use defaults for development
            return {
                'secret_key': 'dev-secret-key-change-in-production',
                'jwt_secret': 'dev-jwt-secret-change-in-production',
                'password_salt': 'dev-salt-change-in-production',
                'environment': 'development',
                'lm_url': os.getenv('BHIV_LM_URL', 'https://api.openai.com/v1'),
                'lm_api_key': os.getenv('BHIV_LM_API_KEY', 'demo-key'),
                'database_url': os.getenv('BHIV_DATABASE_URL', 'sqlite:///data/meta.db'),
                'analytics_enabled': os.getenv('BHIV_ANALYTICS_ENABLED', 'true').lower() == 'true',
                'log_level': os.getenv('BHIV_LOG_LEVEL', 'INFO')
            }
        
        return {
            'secret_key': os.getenv('BHIV_SECRET_KEY'),
            'jwt_secret': os.getenv('BHIV_JWT_SECRET'),
            'password_salt': os.getenv('BHIV_PASSWORD_SALT'),
            'environment': os.getenv('BHIV_ENVIRONMENT', 'production'),
            'lm_url': os.getenv('BHIV_LM_URL'),
            'lm_api_key': os.getenv('BHIV_LM_API_KEY'),
            'database_url': os.getenv('BHIV_DATABASE_URL'),
            'analytics_enabled': os.getenv('BHIV_ANALYTICS_ENABLED', 'true').lower() == 'true',
            'log_level': os.getenv('BHIV_LOG_LEVEL', 'INFO')
        }

# Global config instance
config = SecurityConfig.get_config()