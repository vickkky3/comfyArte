from rest_framework.throttling import UserRateThrottle

class CryptoOpsRateThrottle(UserRateThrottle):
    scope = 'crypto_ops'