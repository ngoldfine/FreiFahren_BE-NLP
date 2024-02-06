import unittest
from collections import defaultdict
from main import extract_ticket_inspector_info
from test_cases import test_cases

red = '\033[91m'
reset = '\033[0m'
gray = '\033[90m'


def format_mismatch(expected, actual, label):
    if expected != actual:
        # Highlight mismatch in red
        return f'{red}{label} Found: {actual} | Expected: {expected}{reset}'
    else:
        # No color for matches
        return f'{label} Found: {actual} | Expected: {expected}'


class TestFindStationAndLineFunction(unittest.TestCase):
    failures = []
    failures_direction = defaultdict(int)
    failures_station = defaultdict(int)
    failures_line = defaultdict(int)
    station_none_when_expected = 0
    line_none_when_expected = 0
    direction_none_when_expected = 0

    @classmethod
    def analyze_failures(cls, failures_dict):
        sorted_failures = sorted(
            failures_dict.items(),
            key=lambda item: item[1],
            reverse=True
        )
        failure_summary = '\n'.join(
            [f'{failure}: {count} times' for failure, count in sorted_failures])
        return failure_summary if failure_summary else 'No data'

    @classmethod
    def tearDownClass(cls):
        print('\n===== Failures Summary =====\n')
        if cls.failures:
            for failure in cls.failures:
                print(failure)
            print(f'\nTotal Failures: {len(cls.failures)}')
        else:
            print('All tests passed successfully!')

        print('\n===== Detailed Analysis =====\n')
        print(f'{red}Direction Failures: {sum(cls.failures_direction.values())}{reset}')
        print(f'Number of not found directions: '
              f'{cls.direction_none_when_expected}\n')
        print('Missclassifications (expected -> found):\n' +
              cls.analyze_failures(cls.failures_direction))
          
        print('\n-------------------------\n')
          
        print(f'{red}Station Failures: {sum(cls.failures_station.values())}{reset}')
        print(f'Number of not found station: '
              f'{cls.station_none_when_expected}\n')
        print('Missclassifications (expected -> found):\n' +
              cls.analyze_failures(cls.failures_station))
          
        print('\n-------------------------\n')
          
        print(f'{red}Line Failures: {sum(cls.failures_line.values())}{reset}')
        print(f'Number of lines not found: '
              f'{cls.line_none_when_expected}\n')
        print('Missclassifications (expected -> found):\n' +
              cls.analyze_failures(cls.failures_line))
        print('=========================\n')

    def test_find_station_and_line(self):
        for text, expected_station, expected_line, expected_direction in test_cases:
            with self.subTest(text=text):
                result = extract_ticket_inspector_info(text)
                if result is None:
                    print(f'Error processing text: {text}')
                    continue

                actual_line = result.get('line')
                actual_direction = result.get('direction')
                actual_station = result.get('station')

                has_mismatch = False
                messages = []
                for prop, actual, expected in [
                    ('line', actual_line, expected_line),
                    ('direction', actual_direction, expected_direction),
                    ('station', actual_station, expected_station)
                ]:
                    messages.append(format_mismatch(
                        expected,
                        actual,
                        prop.capitalize()
                    ))
                    if expected is not None and actual is None:
                        getattr(self.__class__, f'{prop}_none_when_expected', 0)
                        setattr(self.__class__, f'{prop}_none_when_expected',
                                getattr(self.__class__, f'{prop}_none_when_expected')
                                + 1)
                    if actual != expected:
                        has_mismatch = True
                        self.__class__.__dict__[
                            f'failures_{prop}'][f'{expected} -> {actual}'
                                                ] += 1

                if has_mismatch:
                    self.__class__.failures.append(f'''{gray}Input text: {text}
                                                   {reset}\n''' +
                                                   '\n'.join(messages) +
                                                   '\n\n-----------------------------\n'
                                                   )


if __name__ == '__main__':
    unittest.main()
