import json
import os

STATS_FILE = "stats.json"


def load_stats():
    if not os.path.exists(STATS_FILE):
        return {
            "total_api_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "requests_count": 0,
        }
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "total_api_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "requests_count": 0,
        }


def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)


def record_usage(input_tokens, output_tokens, model="gpt-4o"):
    stats = load_stats()

    # GPT-4o pricing (approximate)
    # Input: $2.50 / 1M tokens
    # Output: $10.00 / 1M tokens
    cost_input = (input_tokens / 1_000_000) * 2.50
    cost_output = (output_tokens / 1_000_000) * 10.00
    total_cost = cost_input + cost_output

    stats["total_api_cost"] = stats.get("total_api_cost", 0.0) + total_cost
    stats["total_input_tokens"] = stats.get("total_input_tokens", 0) + input_tokens
    stats["total_output_tokens"] = stats.get("total_output_tokens", 0) + output_tokens
    stats["requests_count"] = stats.get("requests_count", 0) + 1

    save_stats(stats)


def get_stats_text():
    stats = load_stats()
    return (
        f"📊 **API Usage**\n\n"
        f"💰 Total Cost: ${stats.get('total_api_cost', 0):.4f}\n"
        f"📥 Input Tokens: {stats.get('total_input_tokens', 0)}\n"
        f"📤 Output Tokens: {stats.get('total_output_tokens', 0)}\n"
        f"🔄 Total Requests: {stats.get('requests_count', 0)}"
    )

