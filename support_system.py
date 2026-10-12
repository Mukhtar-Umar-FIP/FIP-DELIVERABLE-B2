"""
Customer Support Request System
-------------------------------
A simple program that stores, organises and processes customer support requests.

Data structures used:
- dict  : stores every request (key = request ID) and each customer's details
- set   : remembers which request IDs already exist (stops duplicates)
- deque : a queue, so requests are processed in the order they arrived (FIFO)
- list  : used as a stack for undo (LIFO)
"""

import json
from collections import deque

PRIORITY_ORDER = {"High": 0, "Normal": 1, "Low": 2}
STATUS_ORDER = {"Open": 0, "In Progress": 1, "Resolved": 2}


class SupportSystem:
    def __init__(self):
        self.requests = {}        # request_id -> request dictionary
        self.request_ids = set()  # all IDs used so far
        self.queue = deque()      # IDs waiting to be processed
        self.undo_stack = []      # history of changes

    # ---------- Adding ----------

    def add_request(self, request_id, name, email, issue, date,
                    priority="Normal", status="Open", replies=None):
        """Add a new request. Returns True if added, False if the ID is a duplicate."""
        request_id = request_id.strip()
        if request_id == "" or request_id in self.request_ids:
            return False

        request = {
            "id": request_id,
            "customer": {"name": name, "email": email},
            "issue": issue,
            "date": date,
            "priority": priority,
            "status": status,
            "replies": replies if replies else [],
        }
        self.requests[request_id] = request
        self.request_ids.add(request_id)
        if status != "Resolved":
            self.queue.append(request_id)

        self.undo_stack.append(("add", request_id, None))
        return True

    # ---------- Processing ----------

    def process_next(self):
        """Take the oldest request off the queue and mark it Resolved."""
        if len(self.queue) == 0:
            return None
        request_id = self.queue.popleft()
        request = self.requests[request_id]
        self._save_for_undo("process", request_id)
        request["status"] = "Resolved"
        return request

    def mark_urgent(self, request_id):
        """Set a request's priority to High."""
        if request_id not in self.requests:
            return False
        self._save_for_undo("update", request_id)
        self.requests[request_id]["priority"] = "High"
        return True

    def update_status(self, request_id, new_status):
        """Change the status of a request."""
        if request_id not in self.requests or new_status not in STATUS_ORDER:
            return False
        self._save_for_undo("update", request_id)
        self.requests[request_id]["status"] = new_status
        return True

    def add_reply(self, request_id, message):
        """Add a reply or follow-up message to a request."""
        if request_id not in self.requests or message.strip() == "":
            return False
        self._save_for_undo("update", request_id)
        self.requests[request_id]["replies"].append(message)
        return True

    # ---------- Undo ----------

    def _save_for_undo(self, action, request_id):
        """Push a copy of the request onto the stack before changing it."""
        old = self.requests[request_id]
        old_copy = {
            "id": old["id"],
            "customer": dict(old["customer"]),
            "issue": old["issue"],
            "date": old["date"],
            "priority": old["priority"],
            "status": old["status"],
            "replies": list(old["replies"]),
        }
        self.undo_stack.append((action, request_id, old_copy))

    def undo(self):
        """Reverse the most recent change. Returns a message describing it."""
        if len(self.undo_stack) == 0:
            return "Nothing to undo."

        action, request_id, old_copy = self.undo_stack.pop()

        if action == "add":
            del self.requests[request_id]
            self.request_ids.remove(request_id)
            if request_id in self.queue:
                self.queue.remove(request_id)
            return "Undid adding request " + request_id

        if action == "process":
            self.requests[request_id] = old_copy
            self.queue.appendleft(request_id)  # put it back at the front
            return "Undid processing request " + request_id

        # action == "update"
        self.requests[request_id] = old_copy
        return "Undid update to request " + request_id

    # ---------- Searching ----------

    def search_by_id(self, request_id):
        """Fast search: dictionary lookup, O(1)."""
        return self.requests.get(request_id)

    def linear_search_by_id(self, request_id):
        """Slow search: check every request one by one, O(n). Used for comparison."""
        for request in self.requests.values():
            if request["id"] == request_id:
                return request
        return None

    def search_by_name(self, name):
        """Return all requests whose customer name contains the text (case-insensitive)."""
        name = name.lower()
        results = []
        for request in self.requests.values():
            if name in request["customer"]["name"].lower():
                results.append(request)
        return results

    # ---------- Sorting ----------

    def sort_requests(self, by="date"):
        """Sort using Python's built-in sorted() (Timsort), O(n log n)."""
        return sorted(self.requests.values(), key=lambda r: sort_key(r, by))

    def bubble_sort_requests(self, by="date"):
        """Sort using bubble sort, O(n^2). Used for comparison."""
        items = list(self.requests.values())
        n = len(items)
        for i in range(n):
            for j in range(0, n - i - 1):
                if sort_key(items[j], by) > sort_key(items[j + 1], by):
                    items[j], items[j + 1] = items[j + 1], items[j]
        return items

    # ---------- Loading data ----------

    def load_from_file(self, filename):
        """Load sample requests from a JSON file."""
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            self.add_request(
                item["id"], item["name"], item["email"], item["issue"],
                item["date"], item["priority"], item["status"], item["replies"],
            )
        self.undo_stack.clear()  # loading data is not something to undo


def sort_key(request, by):
    """Return the value used to sort a request."""
    if by == "priority":
        return PRIORITY_ORDER[request["priority"]]
    if by == "status":
        return STATUS_ORDER[request["status"]]
    return request["date"]


def show_replies(replies, index=0):
    """
    Recursion: return the replies as numbered lines, in order.
    Base case: index has reached the end of the list.
    Recursive case: format this reply, then call itself for the next one.
    """
    if index >= len(replies):
        return []
    line = str(index + 1) + ". " + replies[index]
    return [line] + show_replies(replies, index + 1)
