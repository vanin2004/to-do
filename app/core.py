from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "To-Do Application"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    
    # Database
    database_url: str = "postgresql://postgres:12345@localhost:5432/todo_db"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # API
    api_prefix: str = ""
    api_title: str = "Todo Lists API"
    api_description: str = "API for managing todo lists and tasks"
    
    # Slug generation
    slug_max_length: int = 100
    slug_separator: str = "-"
    
    # Task weight
    default_task_weight: float = 1000.0
    weight_increment: float = 1000.0

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Игнорировать дополнительные поля из .env


settings = Settings()