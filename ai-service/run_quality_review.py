import json
from pathlib import Path

from app import create_app


BASE_DIR = Path(__file__).resolve().parent
INPUTS_PATH = BASE_DIR / "quality_review_inputs.json"
OUTPUT_PATH = BASE_DIR / "quality_review_results.json"


def score_describe(body):
    score = 5 if isinstance(body.get("description"), str) and body["description"].strip() else 1
    return score


def score_recommend(body):
    if not isinstance(body, list) or len(body) != 3:
        return 1
    required = {"action_type", "description", "priority"}
    if all(isinstance(item, dict) and required.issubset(item.keys()) for item in body):
        return 5
    return 2


def score_report(body):
    required = {"title", "summary", "overview", "key_items", "recommendations"}
    if not required.issubset(body.keys()):
        return 1
    if isinstance(body["key_items"], list) and isinstance(body["recommendations"], list):
        return 5
    return 2


def main():
    app = create_app()
    client = app.test_client()
    inputs = json.loads(INPUTS_PATH.read_text(encoding="utf-8"))
    results = {}

    for endpoint, values in inputs.items():
        endpoint_path = f"/{endpoint}"
        endpoint_results = []
        for index, value in enumerate(values, start=1):
            response = client.post(endpoint_path, json={"input_text": value})
            body = response.get_json()
            if endpoint == "describe":
                score = score_describe(body)
            elif endpoint == "recommend":
                score = score_recommend(body)
            else:
                score = score_report(body)
            endpoint_results.append(
                {
                    "input_id": index,
                    "status_code": response.status_code,
                    "score_out_of_5": score,
                    "response": body,
                }
            )
        avg_score = round(sum(item["score_out_of_5"] for item in endpoint_results) / len(endpoint_results), 2)
        results[endpoint] = {
            "average_score_out_of_5": avg_score,
            "results": endpoint_results,
        }

    OUTPUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved quality review results to {OUTPUT_PATH}")
    for endpoint, result in results.items():
        print(f"{endpoint}: average_score_out_of_5={result['average_score_out_of_5']}")


if __name__ == "__main__":
    main()
