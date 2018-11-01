# frontline-challenge
My Frontline Education challenge automation solution: a small utility for parsing out strings with nested parentheses in a given format.

# Requirements
* Using Python 2.7.
* `pip install regex`
* `pip install pygogo`

# Approach
* After analyzing the test string, dismantle it chunk by chunk by matching against a particular regular expression while keeping track of the current level of depth.
* Store each of these sub-sections as their own object (Segment) with unique GUIDs pointing back to parent sections.
* At the end of gathering all segments and their relationships, tree can be dynamically reconstructed at the end (to support both direct output & alphabetical output.)
* New test cases can be added within the `tests` directory and executed as part of the group or as one-offs (by providing an individual test case number at the command-line.)

# Assumptions
* Test string is surrounded by parentheses.
* Test string fits on a single line (so no multi-line input supported.)
* Each section / sub-section has starting & ending parentheses (i.e. a matching number of each.)
* Test cases solely in `tests` subfolder.
* Test case folder is not empty when script is executed.
* Each test case file starts with a number followed by an underscore.
* No test case starts with a duplicate number.
* No empty parentheses in valid test case string (i.e. "()").

# Flags
* `-d`: Activate debug mode, displaying all debug-level statements in the console.
* `-t {number}`: Identify an individual test case to run found in the `tests` subfolder. (If not specified, will instead run *all* test cases found in the `tests` subfolder.)
* `-a`: Sort parsed string results alphabetically.

# Post Mortem
* Alternatively, more probably could've been done by attempting a [potentially] simpler implementation, such as tokenizing out the string, processing it character-by-character (and seeking out parentheses to increment/decrement the current depth), or trying to perform character substitution to transition the string into a more workable format (like JSON.)

# Sample Input
```
python main.py -d -t 1 -a
```

# Sample Console Output
```
2018-11-01 00:25:18,378 - INFO:  ------> Executing: tests/1_given_sample.txt <------
2018-11-01 00:25:18,378 - DEBUG: Has Valid Bookends?: True
2018-11-01 00:25:18,378 - DEBUG: Has Even Parentheses?: True
2018-11-01 00:25:18,378 - DEBUG: Has Empty Parentheses?: False
2018-11-01 00:25:18,378 - DEBUG: Depth 0 Bits: ['id,created,employee', ',location']
2018-11-01 00:25:18,378 - DEBUG: Inner Extract: ['(id,firstname,employeeType(id),lastname)']
2018-11-01 00:25:18,381 - DEBUG: Last Segment Details: b96ed6b5-c610-47da-b883-8bef4d28500e, id, None
2018-11-01 00:25:18,381 - DEBUG: Last Segment Details: 70703097-daaf-4c40-a8e5-4cba8f924980, created, None
2018-11-01 00:25:18,381 - DEBUG: Last Segment Details: ad757ff9-a25a-4d08-a1af-99a9c2af74a8, employee, None
2018-11-01 00:25:18,381 - DEBUG: Appending Parent GUID: ad757ff9-a25a-4d08-a1af-99a9c2af74a8
2018-11-01 00:25:18,381 - DEBUG: Last Segment Details: 446a8bf4-8837-4ba1-bd7b-ce10d11dda46, location, None
2018-11-01 00:25:18,381 - DEBUG: Depth 1 Bits: ['id,firstname,employeeType', ',lastname']
2018-11-01 00:25:18,381 - DEBUG: Inner Extract: ['(id)']
2018-11-01 00:25:18,382 - DEBUG: Last Segment Details: 83c4a9d0-4318-41c1-b0f8-3c0b85c021a5, id, ad757ff9-a25a-4d08-a1af-99a9c2af74a8
2018-11-01 00:25:18,382 - DEBUG: Last Segment Details: e70a5f0e-201b-4b6d-84ab-74168062fa76, firstname, ad757ff9-a25a-4d08-a1af-99a9c2af74a8
2018-11-01 00:25:18,382 - DEBUG: Last Segment Details: d20573c1-a492-447a-8289-b84ed3e21710, employeeType, ad757ff9-a25a-4d08-a1af-99a9c2af74a8
2018-11-01 00:25:18,382 - DEBUG: Appending Parent GUID: d20573c1-a492-447a-8289-b84ed3e21710
2018-11-01 00:25:18,382 - DEBUG: Last Segment Details: 5063e309-1114-4c99-92b5-d1586a7ae39b, lastname, ad757ff9-a25a-4d08-a1af-99a9c2af74a8
2018-11-01 00:25:18,382 - DEBUG: Depth 2 Bits: ['id']
2018-11-01 00:25:18,384 - DEBUG: Inner Extract: []
2018-11-01 00:25:18,384 - DEBUG: Last Segment Details: 1880134b-113b-4528-9c65-e0cc0b34c9de, id, d20573c1-a492-447a-8289-b84ed3e21710
2018-11-01 00:25:18,384 - DEBUG: Segment #1: b96ed6b5-c610-47da-b883-8bef4d28500e, id, 0, None, True
2018-11-01 00:25:18,384 - DEBUG: Segment #2: 70703097-daaf-4c40-a8e5-4cba8f924980, created, 0, None, True
2018-11-01 00:25:18,384 - DEBUG: Segment #3: ad757ff9-a25a-4d08-a1af-99a9c2af74a8, employee, 0, None, True
2018-11-01 00:25:18,384 - DEBUG: Segment #4: 446a8bf4-8837-4ba1-bd7b-ce10d11dda46, location, 0, None, True
2018-11-01 00:25:18,384 - DEBUG: Segment #5: 83c4a9d0-4318-41c1-b0f8-3c0b85c021a5, id, 1, ad757ff9-a25a-4d08-a1af-99a9c2af74a8, False
2018-11-01 00:25:18,384 - DEBUG: Segment #6: e70a5f0e-201b-4b6d-84ab-74168062fa76, firstname, 1, ad757ff9-a25a-4d08-a1af-99a9c2af74a8, False
2018-11-01 00:25:18,384 - DEBUG: Segment #7: d20573c1-a492-447a-8289-b84ed3e21710, employeeType, 1, ad757ff9-a25a-4d08-a1af-99a9c2af74a8, False
2018-11-01 00:25:18,384 - DEBUG: Segment #8: 5063e309-1114-4c99-92b5-d1586a7ae39b, lastname, 1, ad757ff9-a25a-4d08-a1af-99a9c2af74a8, False
2018-11-01 00:25:18,384 - DEBUG: Segment #9: 1880134b-113b-4528-9c65-e0cc0b34c9de, id, 2, d20573c1-a492-447a-8289-b84ed3e21710, False
2018-11-01 00:25:18,384 - DEBUG: Parent GUID #1: ad757ff9-a25a-4d08-a1af-99a9c2af74a8
2018-11-01 00:25:18,384 - DEBUG: Parent GUID #2: d20573c1-a492-447a-8289-b84ed3e21710
2018-11-01 00:25:18,384 - INFO: created
2018-11-01 00:25:18,384 - INFO: employee
2018-11-01 00:25:18,384 - INFO: - employeeType
2018-11-01 00:25:18,384 - INFO: -- id
2018-11-01 00:25:18,384 - INFO: - firstname
2018-11-01 00:25:18,384 - INFO: - id
2018-11-01 00:25:18,384 - INFO: - lastname
2018-11-01 00:25:18,384 - INFO: id
2018-11-01 00:25:18,384 - INFO: location
```
