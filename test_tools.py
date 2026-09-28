import unittest

from tools import (
    get_request,
    search_requests,
    get_summary,
)


class TestTools(unittest.TestCase):

    def test_get_existing_request(self):

        result = get_request("1001")

        self.assertEqual(
            result["status"],
            "Open"
        )

        self.assertEqual(
            result["priority"],
            "High"
        )


    def test_get_unknown_request(self):

        result = get_request("9999")

        self.assertIn(
            "error",
            result
        )


    def test_search_requests(self):

        results = search_requests(
            "Water Supply"
        )

        self.assertEqual(
            len(results),
            1
        )


    def test_summary(self):

        result = get_summary()

        self.assertEqual(
            result["total"],
            4
        )

        self.assertEqual(
            result["open"],
            2
        )

        self.assertEqual(
            result["resolved"],
            1
        )


if __name__ == "__main__":
    unittest.main()