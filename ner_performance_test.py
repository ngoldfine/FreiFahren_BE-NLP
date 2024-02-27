import unittest
from NER.TransportInformationRecognizer import TransportInformationRecognizer


class CustomTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_tests = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_tests += 1

    def percentage_passed(self):
        total_tests = self.passed_tests + len(self.failures) + len(self.errors)
        return 100.0 * self.passed_tests / total_tests if total_tests > 0 else 100.0


class CustomTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        result = super().run(test)
        percentage_passed = result.percentage_passed()

        if percentage_passed >= 90:
            emoji = "✅"
        elif percentage_passed >= 70:
            emoji = "🟡"
        elif percentage_passed >= 50:
            emoji = "🔵"
        else:
            emoji = "❌"

        print(f"\nPercentage of passed tests: {percentage_passed:.2f}% {emoji}")
        return result


class TestTransportInformationRecognizerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text_processor = TransportInformationRecognizer('NER/models/loss17')

    @staticmethod
    def generate_test_case(text, expected_stations):
        def test(self):
            result = self.text_processor.process_text(text)
            self.assertEqual(result, expected_stations)
        return test


def generate_tests():
    test_cases = [
        ("Gleisdreieck, on the platform", ["Gleisdreieck"]),
        ("U6 Paradestr Richtung Kurt Schumacher Platz", ["Paradestr", "Kurt Schumacher Platz"]),
        
    ]

    for i, (text, expected_stations) in enumerate(test_cases, start=1):
        test_method = TestTransportInformationRecognizerIntegration.generate_test_case(
            text,
            expected_stations
        )
        test_method_name = f'test_station_extraction_{i}'
        setattr(TestTransportInformationRecognizerIntegration, test_method_name, test_method)


generate_tests()

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner())
