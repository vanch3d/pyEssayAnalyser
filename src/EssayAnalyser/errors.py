from flask import jsonify


class EssayError(Exception):
    """Base class for exceptions in pyEA."""

    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.explanation = ""

    def json(self):
        return jsonify({"error":
            {
                "status": self.status,
                "message": self.message,
                "explanation": self.explanation
            }}
        )
