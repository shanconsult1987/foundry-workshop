import time

from app import ask_agent


def run_monitored_request(question):

    start_time = time.perf_counter()

    try:

        response = ask_agent(question)

        end_time = time.perf_counter()

        latency = end_time - start_time

        print()
        print("==============================")
        print("Performance")
        print("==============================")
        print(f"Latency : {latency:.2f} seconds")
        print("Status  : SUCCESS")
        print()

        return response

    except Exception as error:

        end_time = time.perf_counter()

        latency = end_time - start_time

        print()
        print("==============================")
        print("Performance")
        print("==============================")
        print(f"Latency : {latency:.2f} seconds")
        print("Status  : FAILED")
        print(f"Error   : {error}")
        print()

        raise


def main():

    question = input("Question: ")

    response = run_monitored_request(
        question
    )

    print("Response:")
    print(response)


if __name__ == "__main__":
    main()