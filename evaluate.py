from app import ask_agent


TEST_CASES = [
    {
        "question": "What is the status of request 1001?",
        "expected": ["Open"],
    },
    {
        "question": "What is the priority of request 1001?",
        "expected": ["High"],
    },
    {
        "question": "How many total requests are there?",
        "expected": ["4"],
    },
    {
        "question": "How many requests are resolved?",
        "expected": ["1"],
    },
]


def evaluate_response(response, expected_values):

    response_lower = response.lower()

    return all(
        value.lower() in response_lower
        for value in expected_values
    )


def run_evaluation():

    passed = 0
    total = len(TEST_CASES)

    print()
    print("==============================")
    print(" GenAI Evaluation")
    print("==============================")
    print()

    for test in TEST_CASES:

        response = ask_agent(
            test["question"]
        )

        passed_test = evaluate_response(
            response,
            test["expected"]
        )

        if passed_test:
            passed += 1

        print("--------------------------------")
        print("Question:")
        print(test["question"])

        print()
        print("Expected:")
        print(test["expected"])

        print()
        print("Response:")
        print(response)

        print()
        print(
            "Result:",
            "PASS" if passed_test else "FAIL"
        )

    score = (passed / total) * 100

    print()
    print("==============================")
    print("Evaluation Summary")
    print("==============================")
    print(f"Passed: {passed}/{total}")
    print(f"Score : {score:.1f}%")
    print()


if __name__ == "__main__":
    run_evaluation()