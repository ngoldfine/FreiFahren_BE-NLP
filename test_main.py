import unittest
from collections import defaultdict
from main import extract_ticket_inspector_info
from test_cases import test_cases


def format_mismatch(expected, actual, label):
    red = '\033[91m'
    reset = '\033[0m'
    if expected != actual:
        # Highlight mismatch in red
        return f'{label} Found: {red}{actual}{reset} Expected: {red}{expected}{reset}'
    else:
        # No color for matches
        return f'{label} Found: {actual} Expected: {expected}'


class TestFindStationAndLineFunction(unittest.TestCase):
    failures_direction = defaultdict(int)
    failures_station = defaultdict(int)
    failures_line = defaultdict(int)
    station_none_when_expected = 0
    line_none_when_expected = 0
    direction_none_when_expected = 0

    @classmethod
    def analyze_failures(cls, failures_dict):
        # Sort failures by frequency, descending
        sorted_failures = sorted(
            failures_dict.items(),
            key=lambda item: item[1],
            reverse=True
        )
        if sorted_failures:
            failure_summary = ''
            for failure, count in sorted_failures:
                failure_summary += f'{failure}: {count} times\n'
            return failure_summary
        return 'No data'

    @classmethod
    def tearDownClass(cls):
        sum_station_failures = sum(cls.failures_station.values())
        sum_line_failures = sum(cls.failures_line.values())
        sum_direction_failures = sum(cls.failures_direction.values())

        # Split the calculation of total_failures into multiple lines
        total_failures = (
            sum_station_failures +
            sum_line_failures +
            sum_direction_failures
        )

        print('\n===== Test Summary =====')
        print(f'\033[91mPercentage of failed tests: {total_failures}%\033[0m')

        print('\n-------------------------')

        print(f'\nDirection Failures: {sum_direction_failures}')

        print(f'\nNumber of directions not found: {cls.direction_none_when_expected}')
        
        print('\nMissclassifcation summary: (expected -> found)')
        print(cls.analyze_failures(cls.failures_direction))
        
        print('\n-------------------------')
        
        print(f'\nStation Failures: {sum_station_failures}')
        
        print(f'\nNumber of stations not found: {cls.station_none_when_expected}')
        
        print('\nMissclassifcation summary: (expected -> found)')
        print(cls.analyze_failures(cls.failures_station))
        
        print('\n-------------------------')
        
        print(f'\nLine Failures: {sum_line_failures}')
        
        print(f'\nNumber of lines was not found: {cls.line_none_when_expected}')
        
        print('\nMissclassifcation summary: (expected -> found)')
        print(cls.analyze_failures(cls.failures_line))
        print('=========================')

    def test_find_station_and_line(self):
        for text, expected_station, expected_line, expected_direction in test_cases:
            with self.subTest(text=text):
                result = extract_ticket_inspector_info(text)

                # Always retrieve results for line, direction, and station
                actual_line = result.get('line')
                actual_direction = result.get('direction')
                actual_station = result.get('station')

                # Generate messages for all, highlight mismatches
                messages = [
                    format_mismatch(expected_line, actual_line, 'Line'),
                    format_mismatch(expected_direction, actual_direction, 'Direction'),
                    format_mismatch(expected_station, actual_station, 'Station'),
                ]

                # Determine if there's any mismatch
                has_mismatch = any(
                    expected != actual for expected, actual in [
                        (expected_line, actual_line),
                        (expected_direction, actual_direction),
                        (expected_station, actual_station)
                    ]
                )

                if has_mismatch:
                    self.__class__.failures_line[expected_line] += actual_line != expected_line
                    self.__class__.failures_direction[expected_direction] += actual_direction != expected_direction
                    self.__class__.failures_station[expected_station] += actual_station != expected_station

                    # Increment counters for None mismatches
                    if actual_line is None and expected_line is not None:
                        self.__class__.line_none_when_expected += 1
                    if actual_direction is None and expected_direction is not None:
                        self.__class__.direction_none_when_expected += 1
                    if actual_station is None and expected_station is not None:
                        self.__class__.station_none_when_expected += 1

                    custom_message = f'\nInput text: {text}\n' + '\n'.join(messages)
                    print(custom_message)  # Print detailed output

                    # Force a failure to ensure the test is marked as failed
                    self.fail(custom_message)


if __name__ == '__main__':
    unittest.main()
