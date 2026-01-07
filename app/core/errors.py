#Base error classes for the app

class DomainError(Exception):
    """Base error class for domains"""
    pass


class PersistenceError(Exception):
    """Base error class for persistences (Databases, queries, files)"""
    pass


class InfraError(Exception):
    """Base error class for infrastructure (external services, clients)"""
    pass
