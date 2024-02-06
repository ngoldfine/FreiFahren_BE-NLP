import unittest
from collections import defaultdict
from main import extract_ticket_inspector_info
from test_cases import test_cases


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

                actual_line = result.get('line')
                actual_direction = result.get('direction')
                actual_station = result.get('station')

                if actual_line != expected_line:
                    self.__class__.failures_line[
                        f'{expected_line} -> {actual_line}'
                    ] += 1
                    if actual_line is None:
                        self.__class__.line_none_when_expected += 1

                if actual_direction != expected_direction:
                    self.__class__.failures_direction[
                        f'{expected_direction} -> {actual_direction}'
                    ] += 1
                    if actual_direction is None:
                        self.__class__.direction_none_when_expected += 1

                if actual_station != expected_station:
                    self.__class__.failures_station[
                        f'{expected_station} -> {actual_station}'
                    ] += 1
                    if actual_station is None:
                        self.__class__.station_none_when_expected += 1

                # Failure logs:
                self.assertEqual(actual_line, expected_line,
                                 f'Line mismatch in text: {text}')
                self.assertEqual(actual_direction, expected_direction,
                                 f'Direction mismatch in text: {text}')
                self.assertEqual(actual_station, expected_station,
                                 f'Station mismatch in text: {text}')


if __name__ == '__main__':
    unittest.main()
