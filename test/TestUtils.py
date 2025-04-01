from test.TestResults import TestResults
from test.TestCaseResultDto import TestCaseResultDto
import json
import requests

class TestUtils:
    GUID = "4be53935-1ef8-4657-a6ba-340a3945c38e"
    URL = "https://yaksha-prod-sbfn.azurewebsites.net/api/YakshaMFAEnqueue?code=jSTWTxtQ8kZgQ5FC0oLgoSgZG7UoU9Asnmxgp6hLLvYId/GW9ccoLw=="

    @classmethod
    def yakshaAssert(self, test_name, result, test_type):
        ref = open("../custom.ih", "r")
        customData = ref.read()
        ref.close()
        test_case_results = dict()

        result_status = "Failed"
        result_score = 0
        if result:
            result_status = "Passed"
            result_score = 1

        test_case_result_dto = TestCaseResultDto(test_name, test_type, 1, result_score, result_status, True, "")
        test_case_results[self.GUID] = test_case_result_dto

        test_results = TestResults(json.dumps(test_case_results), customData)

        final_result = json.dumps(test_results)

        requests.post(self.URL, final_result)
