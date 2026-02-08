class FraudDetectionException(Exception):
    pass


class ModelLoadError(FraudDetectionException):
    pass


class DatabaseError(FraudDetectionException):
    pass


class ValidationError(FraudDetectionException):
    pass


class NotFoundError(FraudDetectionException):
    pass
