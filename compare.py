"""
Compares two searching approaches and two sorting approaches.
Run with:  python compare.py
"""

import random
import time

from support_system import SupportSystem

PRIORITIES = ["High", "Normal", "Low"]


def build_system(size):
    system = SupportSystem()
    for i in range(size):
        day = random.randint(1, 28)
        date = "2026-10-" + str(day).zfill(2)
        system.add_request("REQ" + str(i), "Customer " + str(i), "c" + str(i) + "@example.com",
                           "Issue " + str(i), date, random.choice(PRIORITIES))
    return system


def time_it(function, *args):
    start = time.perf_counter()
    function(*args)
    return (time.perf_counter() - start) * 1000  # milliseconds


def main():
    print("Size   | Dict search | Linear search | sorted() | Bubble sort   (all in ms)")
    print("-------+-------------+---------------+----------+------------")
    for size in [100, 1000, 3000]:
        system = build_system(size)
        last_id = "REQ" + str(size - 1)  # worst case for linear search

        dict_ms = time_it(system.search_by_id, last_id)
        linear_ms = time_it(system.linear_search_by_id, last_id)
        sorted_ms = time_it(system.sort_requests, "date")
        bubble_ms = time_it(system.bubble_sort_requests, "date")

        print(f"{size:<6} | {dict_ms:11.4f} | {linear_ms:13.4f} | {sorted_ms:8.3f} | {bubble_ms:10.1f}")


if __name__ == "__main__":
    main()
