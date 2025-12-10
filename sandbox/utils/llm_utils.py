from copy import deepcopy
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

_FEEDBACK_SYSTEM_PROMPT = (
"""
# ROLE
You are an expert AI Educational Assessor. Your goal is to analyze student test data, compare their answers against valid keys, and generate constructive, personalized pedagogical feedback.

# CONTEXT
You will be provided with a JSON dataset representing a student's test session. 
The data contains two specific question types:
1. "clozetext": Fill-in-the-blank questions.
2. "classification": Sorting items into categories.

# INSTRUCTIONS FOR DATA INTERPRETATION

## 1. How to Grade "clozetext"
- Look at `stimulus` to understand the sentence context.
- Compare the student's `response.value` list against the `validation.valid_response.value` AND `validation.alt_responses`.
- If the student's answer matches *any* valid or alternative response, mark it correct.
- If it does not match, identify the grammatical or factual error.

## 2. How to Grade "classification"
- This type relies on **Index Mapping**.
- The `possible_responses` list contains the actual words (e.g., ["Noise", "Annoys", ...]).
- The `response.value` contains arrays of integers. These integers are **indices** referring to the `possible_responses`.
- **Example Logic:** If `response.value` is `[[6], [0, 2]]`:
  - Column 1 contains `possible_responses[6]`.
  - Column 2 contains `possible_responses[0]` and `possible_responses[2]`.
- Compare the student's grouping against the `validation.valid_response` grouping to determine accuracy.

# TASK
For each question in the dataset:
1. Determine if the student was correct, partially correct, or incorrect.
2. Generate 4 specific insights:
   - **Summary:** A brief description of what the student did (e.g., "Correctly identified all nouns and verbs").
   - **Strength:** What specific concept has the student mastered? (e.g., "Strong command of subject-verb agreement").
   - **Weakness:** Where did they struggle? If the answer is 100% correct, state "None observed."
   - **Recommendation:** A specific next step or study tip. If 100% correct, suggest a more advanced challenge.

3. Generate an **Overall Session Assessment** aggregating the performance across all questions.

# CONSTRAINTS
- Output **ONLY** valid JSON. Do not include markdown formatting (like ```json) or conversational text.
- The keys for the specific questions must be dynamic based on the Question ID (e.g., `que_01`, `que_02`).
- Tone: Encouraging, professional, and objective.

# OUTPUT FORMAT
Your output must strictly follow this schema:

{
  "que_[ID]": [
    {"type": "summary", "comment": "..."},
    {"type": "strength", "comment": "..."},
    {"type": "weakness", "comment": "..."},
    {"type": "recommendation", "comment": "..."}
  ],
  ... (repeat for all questions),
  "Overall_Question_Answers": [
    {"type": "overall_question_item_summary", "comment": "..."},
    {"type": "overall_question_item_strength", "comment": "..."},
    {"type": "overall_question_item_weakness", "comment": "..."},
    {"type": "overall_question_item_recommendation", "comment": "..."}
  ]
}
"""
)

_ACTIVITY_GENERATION_SYSTEM_PROMPT = (
""" 
# ROLE
You are an expert Adaptive Learning Content Designer. Your goal is to generate new, targeted practice questions based on specific feedback about a student's previous performance.

# CONTEXT
You will be provided with a **Feedback JSON** containing analysis of a student's strengths, weaknesses, and recommendations for improvement. 
The feedback keys (e.g., `que_01`, `que_05`) correspond to questions of varying types (`clozetext` or `classification`) in no specific order.
Your job is to create a **New Question Set** (in JSON format) that specifically addresses the "recommendation" and "weakness" fields found in the feedback.

# TASK
1. **Analyze & Infer Question Type:**
   - Iterate through every question key in the input JSON (ignoring `Overall_Question_Answers`).
   - Read the `summary` and `recommendation` comments to **infer** the question type:
     - **Clozetext:** Look for keywords like "blank", "gap", "sentence", "tense", "grammar", "verb".
     - **Classification:** Look for keywords like "classify", "group", "sort", "category", "match", "columns".
   - Extract the specific **recommendation** to understand the skill gap (e.g., "Practice irregular verbs" or "Distinguish between nouns and adjectives").

2. **Generate New Content:**
   - For each processed key, generate **one** new question of the **inferred type**.
   - **If Clozetext:** Create a new sentence with blanks that specifically targets the recommended skill.
   - **If Classification:** Create a new grouping task with categories and items that address the specific confusion identified.
   - Ensure the `id` of the new question corresponds to the feedback key (e.g., if feedback was for `que_01`, the new question `id` is "01").

3. **Format the Output:**
   - You must strictly follow the provided schema.
   - **Important for Classification:** You must generate the `possible_responses` list (the words/items) AND the `valid_response` (the correct grouping).
   - **Crucial Logic:** The `valid_response` values are **indices**. If "Apple" is the first word in `possible_responses` (index 0) and it belongs in Column 1, then `valid_response[0]` must contain `0`.

# SCHEMA & CONSTRAINTS
Output a single JSON array containing the new questions. Adhere strictly to this structure:

```json
[
  {
    "id": "01",
    "question": {
      "type": "clozetext",
      "instant_feedback": true, 
      "stimulus": "<p>[Insert instruction, e.g., 'Fill in the blanks using the correct past tense form.']</p>",
      "template": "<p>[Insert sentence with {{response}} placeholders]</p>",
      "max_length": 15,
      "validation": {
        "scoring_type": "exactMatch",
        "alt_responses": [],
        "valid_response": {
          "score": 1,
          "value": ["[Correct Answer 1]", "[Correct Answer 2]"]
        }
      }
    },
    "response": { "value": [] }
  },
  {
    "id": "02",
    "question": {
      "type": "classification",
      "instant_feedback": true,
      "stimulus": "<p>[Insert instruction, e.g., 'Classify the following words...']</p>",
      "ui_style": {
        "column_count": 2, 
        "column_titles": ["[Category A]", "[Category B]"]
      },
      "validation": {
        "scoring_type": "exactMatch",
        "valid_response": {
          "score": 1,
          "value": [
            [0, 2], 
            [1, 3] 
          ]
        }
      },
      "possible_responses": ["Word A", "Word B", "Word C", "Word D"]
    },
    "response": { "value": [] }
  }
]```
"""
)

activity_feedback = None

def _configure_llm_client() -> tuple[OpenAI, str]:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set; update your .env file before running this script.")

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("OPENAI_MODEL")
    return client, model_name

def _build_user_prompt(user_data):
    return f"""
    # INPUT DATA
    ###
    {user_data}
    ###
    """

def _send_llm_request(system_prompt, user_prompt, temperature=1.0):
    client, model_name = _configure_llm_client()
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("The model returned an empty response; try a different model or rerun the request.")
    
    return json.loads(content)

def _extract_question_entries(raw_payload):
  """Return a list of question entries from various payload layouts."""

  candidates = None

  if isinstance(raw_payload, list):
    candidates = raw_payload
  elif isinstance(raw_payload, dict):
    for key in ("questions", "result", "items", "data"):
      value = raw_payload.get(key)
      if isinstance(value, list):
        candidates = value
        break
  else:
    raise ValueError("Unsupported payload type; expected dict or list.")

  if candidates is None:
    raise ValueError("Payload must include a list under 'questions', 'result', 'items', or 'data'.")

  for entry in candidates:
    if not isinstance(entry, dict):
      raise ValueError("Each question entry must be a dictionary.")

  return candidates

def _convert_questions_to_activity(new_questions_payload):
  """Convert generated question data into a Learnosity activity payload."""

  items = []
  questions = []

  for question_entry in _extract_question_entries(new_questions_payload):
    question_id = question_entry.get("id")
    question_data = question_entry.get("question")

    if not question_id or not isinstance(question_id, str):
      raise ValueError("Each question entry requires an 'id' string.")
    if not isinstance(question_data, dict):
      raise ValueError("Each question entry requires a 'question' dictionary.")

    response_id = f"generated_{question_id}"

    items.append(
      {
        "content": f"<span class='learnosity-response question-{response_id}'></span>",
        "response_ids": [response_id],
        "workflow": "",
        "reference": f"item-{question_id}",
      }
    )

    question_payload = deepcopy(question_data)
    question_payload["response_id"] = response_id
    question_payload.setdefault("description", "")
    questions.append(question_payload)

  return {
    "items": items,
    "questionsApiActivity": {
      "consumer_key": os.getenv("LEARNOSITY_CONSUMER_KEY", "INSERT_CONSUMER_KEY_HERE"),
      "timestamp": os.getenv("LEARNOSITY_TIMESTAMP", "INSERT_CURRENT_TIMESTAMP_HERE"),
      "signature": os.getenv("LEARNOSITY_SIGNATURE", "INSERT_GENERATED_SIGNATURE_HERE"),
      "user_id": os.getenv("LEARNOSITY_USER_ID", "demo_user"),
      "type": "submit_practice",
      "state": "initial",
      "id": os.getenv("LEARNOSITY_ACTIVITY_ID", "generated_practice"),
      "name": os.getenv("LEARNOSITY_ACTIVITY_NAME", "Generated Practice"),
      "questions": questions,
    },
  }

def get_llm_feedback(report_data):
    global activity_feedback
    activity_feedback = _send_llm_request(system_prompt=_FEEDBACK_SYSTEM_PROMPT, user_prompt=_build_user_prompt(report_data))
    return activity_feedback

def generate_practice_activity():
    new_questions = _send_llm_request(system_prompt=_ACTIVITY_GENERATION_SYSTEM_PROMPT, user_prompt=_build_user_prompt(activity_feedback))
    new_activity = _convert_questions_to_activity(new_questions)
    return new_activity
