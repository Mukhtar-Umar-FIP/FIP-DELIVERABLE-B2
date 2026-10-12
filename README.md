# FIP Deliverable B2: Customer Support Request System

A simple Python program that receives, organises and processes customer support requests.
The logic is plain Python, and the front end is an HTML page served by Flask.

## Features

- Add a new support request
- Store customer information in dictionaries
- Stop duplicate request IDs with a set
- Process requests in the order they arrive with a queue
- Mark urgent requests as High priority
- Undo the most recent change with a stack
- Search for a request by ID or customer name
- Sort requests by date, priority or status
- Show replies and follow-up messages in order with a recursive function
- Compare two searching approaches and two sorting approaches

## Project Structure

```
support_system.py            Main program logic (all the data structures)
app.py                       Flask web server that connects the logic to the HTML pages
templates/index.html         Main page: add, queue, undo, search, sort
templates/request.html       Single request page: details and replies
static/style.css             Page styling
data/sample_requests.json    Sample support-request data (8 requests)
tests/test_support_system.py Automated tests (25 tests)
compare.py                   Times the searching and sorting approaches
```

## Setup and How to Run

You need Python 3.8 or newer.

1. Clone the repository:
   ```
   git clone https://github.com/Mukhtar-Umar-FIP/FIP-DELIVERABLE-B2.git
   cd FIP-DELIVERABLE-B2
   ```
2. (Optional) Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (Mac/Linux)
   ```
3. Install Flask:
   ```
   pip install -r requirements.txt
   ```
4. Start the program:
   ```
   python app.py
   ```
5. Open **http://127.0.0.1:5000** in your browser.

The program loads the sample data from `data/sample_requests.json` when it starts.

### Running the tests

```
python -m unittest discover tests
```

### Running the comparison

```
python compare.py
```

## How to Use

| Task | How |
|------|-----|
| Add a request | Fill in the "Add a Request" form and click **Add Request** |
| Process the next request | Click **Process Next Request**. The oldest request in the queue is marked Resolved |
| Mark as urgent | Click **Mark Urgent** next to a request |
| Change status | Choose a status next to a request and click **Set** |
| Undo | Click **Undo Last Change** |
| Search | Type an ID (e.g. `REQ002`) or part of a name (e.g. `amina`) and click **Search** |
| Sort | Click **Date**, **Priority** or **Status** |
| View or add replies | Click a request ID to open its page |

## Data Structures Used

| Feature | Data structure | Why it was chosen |
|---------|----------------|-------------------|
| Store requests | Dictionary (`dict`), key = request ID | Finding, updating or deleting a request by ID takes O(1) time on average |
| Store customer information | Dictionary (`{"name": ..., "email": ...}`) | Each field has a clear name, so the code is easy to read |
| Stop duplicate IDs | Set (`set`) | Checking whether an ID already exists takes O(1) time on average |
| Process in order received | Queue (`collections.deque`) | First in, first out. `popleft()` is O(1), while `list.pop(0)` is O(n) |
| Undo last change | Stack (Python `list`) | Last in, first out. The most recent change is undone first. `append` and `pop` are O(1) |
| Replies and follow-ups | List + recursion | A list keeps messages in order. The recursive `show_replies()` prints them one at a time |
| Priority and status sorting | Dictionary that maps each value to a number | Turns "High/Normal/Low" into 0/1/2 so they sort in a meaningful order |

## Time and Space Complexity

n = number of requests, r = number of replies on one request.

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| Add request | O(1) | O(1) per request | Dictionary insert + set check + queue append |
| Duplicate check | O(1) | O(n) for the set | Set lookup |
| Process next | O(1) | O(1) | `deque.popleft()` |
| Mark urgent / update status | O(r) | O(r) | O(1) dictionary lookup, plus copying the request (and its r replies) for undo |
| Undo | O(1) usually | O(1) | O(n) only when undoing an "add" that is still in the queue (`deque.remove`) |
| Search by ID (dictionary) | O(1) | O(1) | Hash lookup |
| Search by ID (linear) | O(n) | O(1) | Checks each request one by one |
| Search by name | O(n) | O(k) for k matches | Must check every name because partial matches are allowed |
| Sort with `sorted()` | O(n log n) | O(n) | Timsort |
| Sort with bubble sort | O(n²) | O(n) | Copies the list, then swaps neighbours |
| Show replies (recursive) | O(r²) | O(r) | O(r) calls deep. Joining the lists adds the extra r factor |
| Whole system | n/a | O(n + total replies) | Dict, set, queue and undo stack each grow with n |

## Comparison of Searching and Sorting Approaches

Results from `python compare.py` (times in milliseconds; your numbers will vary):

| Requests | Dict search | Linear search | `sorted()` | Bubble sort |
|----------|-------------|---------------|------------|-------------|
| 100 | 0.0014 | 0.0069 | 0.031 | 1.1 |
| 1,000 | 0.0030 | 0.0634 | 0.340 | 197.2 |
| 3,000 | 0.0029 | 0.2169 | 1.067 | 1,936.0 |

**Searching.** The dictionary lookup (`search_by_id`) stays about the same speed however many requests there are, because it jumps straight to the item using a hash. Linear search (`linear_search_by_id`) checks every request in turn, so its time grows in step with n. The program uses the dictionary search for IDs. Searching by name still has to be linear, because a partial name like "ami" cannot be looked up in a hash.

**Sorting.** Python's built-in `sorted()` uses Timsort, which is O(n log n). Bubble sort compares and swaps neighbours repeatedly, which is O(n²). At 3,000 requests bubble sort was over 1,000 times slower. Both give the same result (a test checks this), but the program uses `sorted()`. Bubble sort is kept only for the comparison.

## Limitations and Possible Improvements

**Limitations**
- Data is kept in memory only. Changes are lost when the program stops (the sample file is not modified).
- Only one person can use it safely at a time. There is no login and no locking for several users.
- Undo only goes backwards. There is no "redo".
- The queue is strictly first-come, first-served. Urgent requests are not moved to the front.
- Searching by name is linear (O(n)), and only simple partial-text matching is supported.
- Input checks are basic (for example, dates are not validated beyond the HTML date picker).

**Possible improvements**
- Save data to a file or a database (for example SQLite) so changes are kept.
- Use a priority queue (`heapq`) so High priority requests are processed first.
- Add a redo stack.
- Add user accounts so agents and customers have different views.
- Build a name index (dictionary of name → list of IDs) to make exact-name searches faster.
- Store replies as a tree so follow-ups can have their own follow-ups, displayed recursively.
