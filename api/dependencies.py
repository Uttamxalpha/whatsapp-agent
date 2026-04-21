from agents.graph import compiled_graph
from config.settings import settings


def get_graph() -> object:
    """Return the compiled LangGraph instance."""
    return compiled_graph


def get_settings() -> object:
    """Return the application settings instance."""
    return settings
