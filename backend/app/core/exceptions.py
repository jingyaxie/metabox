class ApiKeyNotFoundError(Exception):
    """API密钥不存在"""
    pass


class ApiKeyExpiredError(Exception):
    """API密钥已过期"""
    pass


class ApiKeyInactiveError(Exception):
    """API密钥已停用"""
    pass


class QuotaExceededError(Exception):
    """配额已用完"""
    pass


class RateLimitExceededError(Exception):
    """请求频率超限"""
    pass 