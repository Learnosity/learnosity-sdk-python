from docs.quickstart import config
from learnosity_sdk.request import DataApi

itembank_uri = "https://data.learnosity.com/latest-lts/sessions/responses"

security_packet = {
    "consumer_key": config.consumer_key,
    "domain": "localhost",
}


def get_report_data(user_id, session_id):
    # Get response_ids from Data API
    data_api = DataApi()
    data_request = {
        "user_id": [user_id],
        "session_id": [session_id],
        "activity_id": ["quickstart_examples_activity_001"],
        "limit": 10,
    }
    result = data_api.request(
        itembank_uri, security_packet, config.consumer_secret, data_request, "get"
    )
    response = result.json()
    # `response`` here contains the questions and responses for an activity.
    # The format is slightly different to the private network requests in the
    # network requests against the questionresponses API we were looking at.

    with open("sandbox/question_answer_dump.json", "r") as f:
        report_data = f.read()

    return report_data

