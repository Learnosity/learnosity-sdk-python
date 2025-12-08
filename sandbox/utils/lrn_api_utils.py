def get_report_data(user_id, session_id):
    with open('sandbox/question_answer_dump.json', 'r') as f:
        report_data = f.read()

    return report_data