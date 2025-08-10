from fastapi.templating import Jinja2Templates
import json

# Initialize templates with custom filters
templates = Jinja2Templates(directory="app/templates")

def from_json_filter(value):
    """Custom Jinja2 filter to parse JSON strings"""
    try:
        if isinstance(value, str):
            return json.loads(value)
        return value
    except (json.JSONDecodeError, TypeError):
        return {}

# Add custom filter
templates.env.filters['from_json'] = from_json_filter