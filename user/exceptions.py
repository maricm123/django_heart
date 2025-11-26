from apis.exceptions import DomainError


class CannotDeleteClientWhileInActiveTrainingSession(DomainError):
    default_message = "Cannot delete client when in active training session"
    default_code = "delete_error"
    default_status_code = 500
