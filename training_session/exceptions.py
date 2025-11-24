from apis.exceptions import DomainError


class TrainingSessionMetricsProcessingError(DomainError):
    default_message = "Failed to process training metrics."
    default_code = "metrics_processing_error"
    default_status_code = 500
