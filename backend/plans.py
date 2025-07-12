# Centralized place to define plan limits and features.
# This makes it easy to update pricing tiers without changing business logic code.

# Max file size in bytes
MB = 1024 * 1024
PLAN_LIMITS = {
    "free": {
        "monthly_word_limit": 5000,
        "max_file_size": 2 * MB,
        "scan_limit_per_file": 1000, # words
        "humanizer_usage_percent": 0.10, # 10% of monthly word limit can be used for humanizer
        "can_download_report": False,
        "can_view_history": False,
        "api_access": False,
    },
    "pro_basic": {
        "monthly_word_limit": 100000, # Max of the 50k-100k range
        "max_file_size": 30 * MB,
        "scan_limit_per_file": float('inf'), # Unlimited
        "humanizer_usage_percent": 0.50, # 50%
        "can_download_report": True,
        "can_view_history": True,
        "api_access": False,
    },
    "pro_advanced": {
        "monthly_word_limit": 150000, # Max of the 100k-150k range
        "max_file_size": 50 * MB,
        "scan_limit_per_file": float('inf'),
        "humanizer_usage_percent": 0.70, # 70%
        "can_download_report": True,
        "can_view_history": True,
        "api_access": False,
    },
    "enterprise": {
        "monthly_word_limit": float('inf'), # Effectively unlimited, or a very high number
        "max_file_size": 500 * MB,
        "scan_limit_per_file": float('inf'),
        "humanizer_usage_percent": float('inf'), # Unlimited
        "can_download_report": True,
        "can_view_history": True,
        "api_access": True,
    }
}

def get_plan_limits(plan_name: str) -> dict:
    """
    Returns the limits for a given plan name.
    Defaults to 'free' plan if the plan name is not found.
    """
    return PLAN_LIMITS.get(plan_name, PLAN_LIMITS["free"])
