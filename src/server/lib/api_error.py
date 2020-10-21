class ApiError(Exception):
    status = 0
    message = ''

    def __init__(self, status, message):
        self.status = status
        self.message = message
