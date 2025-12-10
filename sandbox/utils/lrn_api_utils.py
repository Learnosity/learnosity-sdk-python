from docs.quickstart import config
from learnosity_sdk.request import DataApi

responses_uri = "https://data.learnosity.com/latest-lts/sessions/responses"
questions_uri = "https://data.learnosity.com/latest-lts/itembank/questions"

security_packet = {
    "consumer_key": config.consumer_key,
    "domain": "localhost",
}


def get_report_data(user_id, session_id):
    # Get responses from Data API
    data_api = DataApi()
    responses_request = {
        "user_id": [user_id],
        "session_id": [session_id],
        "activity_id": ["quickstart_examples_activity_001"],
        "limit": 10,
    }
    responses_result = data_api.request(
        responses_uri, security_packet, config.consumer_secret, responses_request, "get"
    ).json()

    # Get questions from Data API
    question_references = [
        response["question_reference"]
        for response in responses_result["data"][0]["responses"]
    ]
    questions_request = {"references": question_references}
    question_result = data_api.request(
        questions_uri, security_packet, config.consumer_secret, questions_request, "get"
    ).json()

    # Index the responses and questions by question reference
    responses_by_question_reference = dict()
    for response in responses_result["data"][0]["responses"]:
        question_reference = response["question_reference"]
        responses_by_question_reference[question_reference] = response

    questions_by_question_reference = dict()
    for question in question_result["data"]:
        question_reference = question["reference"]
        questions_by_question_reference[question_reference] = question["data"]

    # Build up report_data for LLM
    report_data = []
    for idx, question_reference in enumerate(responses_by_question_reference.keys()):
        response = responses_by_question_reference[question_reference]
        question = questions_by_question_reference[question_reference]
        report_data_entry = {"id": idx}

        report_data_entry["question"] = question
        report_data_entry["response"] = {"value": response["response"]["value"]}
        report_data.append(report_data_entry)

    return report_data
