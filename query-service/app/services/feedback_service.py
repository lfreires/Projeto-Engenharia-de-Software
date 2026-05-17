from app.schemas.chat import FeedbackRequest, FeedbackResponse


class InMemoryFeedbackStore:
    def __init__(self) -> None:
        self._feedback: dict[str, FeedbackRequest] = {}

    def submit(self, request: FeedbackRequest) -> FeedbackResponse:
        self._feedback[request.message_id] = request
        return FeedbackResponse(accepted=True, message_id=request.message_id)
