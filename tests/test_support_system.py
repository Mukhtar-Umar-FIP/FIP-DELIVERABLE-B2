import os
import sys
import unittest

# Let the tests import support_system.py from the project folder
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from support_system import SupportSystem, show_replies

DATA_FILE = os.path.join(PROJECT_DIR, "data", "sample_requests.json")


class TestSupportSystem(unittest.TestCase):

    def setUp(self):
        self.system = SupportSystem()
        self.system.add_request("R1", "Alice", "alice@example.com", "Login problem", "2026-10-03", "Normal")
        self.system.add_request("R2", "Bob", "bob@example.com", "Refund", "2026-10-01", "Low")
        self.system.add_request("R3", "Alice Smith", "alice.s@example.com", "App crash", "2026-10-02", "High")

    # Adding and duplicates
    def test_add_request(self):
        self.assertTrue(self.system.add_request("R4", "Dan", "dan@example.com", "Help", "2026-10-04"))
        self.assertIn("R4", self.system.requests)
        self.assertIn("R4", self.system.request_ids)

    def test_customer_stored_as_dictionary(self):
        customer = self.system.requests["R1"]["customer"]
        self.assertEqual(customer, {"name": "Alice", "email": "alice@example.com"})

    def test_duplicate_id_rejected(self):
        self.assertFalse(self.system.add_request("R1", "Eve", "eve@example.com", "Copy", "2026-10-05"))
        self.assertEqual(self.system.requests["R1"]["customer"]["name"], "Alice")
        self.assertEqual(len(self.system.requests), 3)

    def test_empty_id_rejected(self):
        self.assertFalse(self.system.add_request("  ", "Eve", "eve@example.com", "Blank", "2026-10-05"))

    # Queue
    def test_process_in_order_received(self):
        self.assertEqual(self.system.process_next()["id"], "R1")
        self.assertEqual(self.system.process_next()["id"], "R2")
        self.assertEqual(self.system.process_next()["id"], "R3")
        self.assertIsNone(self.system.process_next())

    def test_processed_request_is_resolved(self):
        done = self.system.process_next()
        self.assertEqual(done["status"], "Resolved")

    # Priority and status
    def test_mark_urgent(self):
        self.assertTrue(self.system.mark_urgent("R2"))
        self.assertEqual(self.system.requests["R2"]["priority"], "High")

    def test_mark_urgent_unknown_id(self):
        self.assertFalse(self.system.mark_urgent("NOPE"))

    def test_update_status(self):
        self.assertTrue(self.system.update_status("R1", "In Progress"))
        self.assertEqual(self.system.requests["R1"]["status"], "In Progress")
        self.assertFalse(self.system.update_status("R1", "Banana"))

    # Undo
    def test_undo_mark_urgent(self):
        self.system.mark_urgent("R2")
        self.system.undo()
        self.assertEqual(self.system.requests["R2"]["priority"], "Low")

    def test_undo_add(self):
        self.system.undo()  # undoes adding R3
        self.assertNotIn("R3", self.system.requests)
        self.assertNotIn("R3", self.system.request_ids)
        self.assertNotIn("R3", self.system.queue)

    def test_undo_process_puts_request_back_at_front(self):
        self.system.process_next()
        self.system.undo()
        self.assertEqual(self.system.queue[0], "R1")
        self.assertEqual(self.system.requests["R1"]["status"], "Open")

    def test_undo_reply(self):
        self.system.add_reply("R1", "Agent: hello")
        self.system.undo()
        self.assertEqual(self.system.requests["R1"]["replies"], [])

    def test_undo_most_recent_first(self):
        self.system.mark_urgent("R1")
        self.system.update_status("R1", "Resolved")
        self.system.undo()
        self.assertEqual(self.system.requests["R1"]["status"], "Open")
        self.assertEqual(self.system.requests["R1"]["priority"], "High")

    def test_undo_when_empty(self):
        empty = SupportSystem()
        self.assertEqual(empty.undo(), "Nothing to undo.")

    # Searching
    def test_search_by_id(self):
        self.assertEqual(self.system.search_by_id("R2")["customer"]["name"], "Bob")
        self.assertIsNone(self.system.search_by_id("NOPE"))

    def test_linear_search_matches_dict_search(self):
        for request_id in ["R1", "R2", "R3", "NOPE"]:
            self.assertEqual(self.system.linear_search_by_id(request_id),
                             self.system.search_by_id(request_id))

    def test_search_by_name(self):
        results = self.system.search_by_name("alice")
        ids = [r["id"] for r in results]
        self.assertEqual(ids, ["R1", "R3"])

    # Sorting
    def test_sort_by_date(self):
        ids = [r["id"] for r in self.system.sort_requests("date")]
        self.assertEqual(ids, ["R2", "R3", "R1"])

    def test_sort_by_priority(self):
        ids = [r["id"] for r in self.system.sort_requests("priority")]
        self.assertEqual(ids, ["R3", "R1", "R2"])

    def test_sort_by_status(self):
        self.system.update_status("R1", "Resolved")
        self.system.update_status("R2", "In Progress")
        ids = [r["id"] for r in self.system.sort_requests("status")]
        self.assertEqual(ids, ["R3", "R2", "R1"])

    def test_bubble_sort_matches_builtin_sort(self):
        for by in ["date", "priority", "status"]:
            self.assertEqual(self.system.bubble_sort_requests(by), self.system.sort_requests(by))

    # Recursion
    def test_show_replies_in_order(self):
        lines = show_replies(["first", "second", "third"])
        self.assertEqual(lines, ["1. first", "2. second", "3. third"])

    def test_show_replies_empty(self):
        self.assertEqual(show_replies([]), [])

    # Sample data
    def test_load_sample_data(self):
        system = SupportSystem()
        system.load_from_file(DATA_FILE)
        self.assertEqual(len(system.requests), 8)
        self.assertEqual(system.undo_stack, [])
        self.assertNotIn("REQ003", system.queue)  # already resolved


if __name__ == "__main__":
    unittest.main()
