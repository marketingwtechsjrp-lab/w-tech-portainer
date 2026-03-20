import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / "settings.json"

DEFAULT_SETTINGS = {
    "ai_provider": "openrouter",
    "api_key": "",
    "model": "anthropic/claude-3.5-sonnet:beta",
    "token_usage_input": 0,
    "token_usage_output": 0,
    "token_cost_usd": 0.0
}

def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            # Merge with defaults to ensure all keys exist
            for key, value in DEFAULT_SETTINGS.items():
                if key not in data:
                    data[key] = value
            return data
        except json.JSONDecodeError:
            return DEFAULT_SETTINGS

def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def get_setting(key: str, default=None):
    return load_settings().get(key, default)

def update_setting(key: str, value) -> None:
    settings = load_settings()
    settings[key] = value
    save_settings(settings)

def register_token_usage(prompt_tokens: int, completion_tokens: int, cost_per_1k_prompt: float = 0.0, cost_per_1k_comp: float = 0.0) -> None:
    settings = load_settings()
    settings["token_usage_input"] = settings.get("token_usage_input", 0) + prompt_tokens
    settings["token_usage_output"] = settings.get("token_usage_output", 0) + completion_tokens
    
    # Optional cost calculation (OpenRouter charges vary heavily per model, this is just an estimate if given)
    added_cost = (prompt_tokens / 1000) * cost_per_1k_prompt + (completion_tokens / 1000) * cost_per_1k_comp
    settings["token_cost_usd"] = settings.get("token_cost_usd", 0.0) + added_cost
    
    save_settings(settings)
