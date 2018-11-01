import sys, os, glob, regex, argparse, logging, uuid
from enum import Enum
from operator import attrgetter
import pygogo as gogo

# TODO: REMOVE THIS!!!
master_string = "(id,created,employee(id,firstname,employeeType(id), lastname),location)"

# Declare our crucial regular expressions to enable us to parse:
parens_check_regex = r'^\(.*\)$'
nest_extract_regex = r'\((?>[^()]+|(?R))*\)'

# Define our pre-testing depth & underlying structure:
depth_level = -1
in_debug_mode = False
test_case_filepaths = []
test_case_numbers = []
segment_list = []
parent_guids_list = []
test_bits = []
parent_guids_by_depth_dict = {}

class ExecutionType(Enum):
	SINGLE = 1
	ALL = 2

class Segment():
	def __init__(self, name, depth, parent):
		self.id = str(uuid.uuid4())
		self.name = name
		self.depth = depth
		self.parent = parent
		self.is_root = True if self.depth == 0 else False
		self.has_processed = False

def configure_parser(parser):
	parser.add_argument('-t', '--test-number', type=int, help='number of the specific test to run')
	parser.add_argument('-a', '--alphabetical-order', help='sort test output alphabetically', action='store_true')
	parser.add_argument('-d', '--debug', help='print full debug statements', action='store_true')

def check_folder_validity():
	# Compile all test case names from the 'tests' subfolder:
	for filepath in glob.glob("tests/*.txt"):
		test_case_filepaths.append(os.path.basename(filepath))

	is_valid = True

	# Check files for correct `#_` format:
	for filename in test_case_filepaths:
		if not filename.startswith('_') and filename.count('_') > 1:
			test_case_numbers.append(filename.split('_')[0])
		else:
			is_valid = False
			break

	# Check for test case number uniqueness:
	if is_valid:
		is_valid = True if len(set(test_case_numbers)) == len(test_case_numbers) else False

	# Check that each test case file starts with a number:
	if is_valid:
		for number in test_case_numbers:
			if not number.isdigit():
				is_valid = False
				break

	return is_valid

def check_test_validity():
	has_valid_bookends = bool(regex.match(parens_check_regex, master_string))
	has_valid_parens_count = True if master_string.count('(') == master_string.count(')') else False
	has_empty_parens = False if master_string.find('()') == -1 else True

	if in_debug_mode:
		logger.debug("Has Valid Bookends?: " + str(has_valid_bookends))
		logger.debug("Has Even Parentheses?: " + str(has_valid_parens_count))
		logger.debug("Has Empty Parentheses?: " + str(has_empty_parens))

	return True if has_valid_bookends and has_valid_parens_count and not has_empty_parens else False

def gather_segments(string, depth_level, test_bits):
	regex_find_count = len(regex.findall(nest_extract_regex, string))
	recursion_anchor = parent_guids_by_depth_dict[depth_level] if depth_level in parent_guids_by_depth_dict else len(parent_guids_list)
	depth_level += 1

	for test_string in regex.findall(nest_extract_regex, string):
		# Calculate total number of sections from regex 'findall' match:
		if regex_find_count > 1:
			parent_guid = parent_guids_list[recursion_anchor - regex_find_count]
			regex_find_count -= regex_find_count
		else:
			if not depth_level == 0:
				parent_guid = parent_guids_list[recursion_anchor - 1]
			else:
				parent_guid = None

		# Strip away parenthetical bookends:
		test_string = test_string[1:len(test_string) - 1]

		# Split out regex bits between parentheses for this section of the depth level:
		depth_bits = regex.split(nest_extract_regex, test_string)

		# Reassign new 'findall' matches back to testing string for later recursive use:
		test_string = str(regex.findall(nest_extract_regex, test_string))

		if in_debug_mode:
			logger.debug("Depth " + str(depth_level) + " Bits: " + str(depth_bits))
			logger.debug("Inner Extract: " + str(test_string))

		# For each depth bit, 
		for idx, section in enumerate(depth_bits):
			last_guid = None

			# Keep but don't calculate any empty sections (since it infers a parent
			# from the previous bit):
			for bit in section.split(','):
				if not bit == '':
					segment = Segment(bit, depth_level, parent_guid)
					last_guid = segment.id

					segment_list.append(segment)

					if in_debug_mode:
						logger.debug("Last Segment Details: " + segment.id + ", " + segment.name + 
							", " + str(segment.parent))

			# Add our parent GUID to the list to tie back to later if it's not empty
			# or out-of-range:
			if last_guid is not None and not (idx + 1) == len(depth_bits):
				parent_guids_list.append(last_guid)

				if in_debug_mode:
					logger.debug("Appending Parent GUID: " + last_guid)

		# Add a bookmark for coming back at a later recursion:
		parent_guids_by_depth_dict[depth_level] = len(parent_guids_list)

		# Recurse between each parenthetical section to reconstruct a Segment tree:
		gather_segments(test_string, depth_level, test_bits)

def print_segments(segment_list):
	for segment in segment_list:
		if segment.has_processed == False:
			segment_output_name = ('-' * segment.depth)
			segment_output_name += (" " + segment.name) if segment.depth else segment.name

			logger.info(segment_output_name)
			segment.has_processed = True

			for potential_child in segment_list:
				iterate_child_segments(segment_list, potential_child, segment)

def iterate_child_segments(segment_list, potential_child, segment):
	# No need to re-process any children already accounted for:
	if potential_child.has_processed == False:
		if segment.id == potential_child.parent:
			child_output_name = ('-' * potential_child.depth) + " " + potential_child.name
			logger.info(child_output_name)
			potential_child.has_processed = True

			# Check back through to see if this child has any children of its own:
			for child in segment_list:
				iterate_child_segments(segment_list, child, potential_child)

def display_output():
	if in_debug_mode:
		segment_index = 1

		# In debug mode, show each segment gathered by the end with all related data:
		for segment in segment_list:
			logger.debug("Segment #" + str(segment_index) + ": " + segment.id + ", " + segment.name + ", " +
				str(segment.depth) + ", " + str(segment.parent) + ", " + str(segment.is_root))
			segment_index += 1

		parent_guid_index = 1

		# In debug mode, show each parent GUID gathered by the end with all related data:
		for guid in parent_guids_list:
			logger.debug("Parent GUID #" + str(parent_guid_index) + ": " + guid)
			parent_guid_index += 1

	# Sort the list alphabetically before visually recreating the tree if flag is set:
	if args['alphabetical_order']:
		segment_list.sort(key=attrgetter('depth', 'name'))

	print_segments(segment_list)

def reset_state():
	# Reset structural variables between case runs when in ExecutionType.ALL mode:
	depth_level = -1
	del segment_list[:]
	del parent_guids_list[:]
	del test_bits[:]

	for key,value in parent_guids_by_depth_dict.items():
		parent_guids_by_depth_dict.pop(key)

if __name__ == "__main__":
	# Configure argument parser & gather any command-line arguments:
	parser = argparse.ArgumentParser(description='Automated tool to print string details by depth.')
	configure_parser(parser)
	args = vars(parser.parse_args())

	# Configure our pygogo logger to prettify our console output:
	log_format = '%(asctime)s - %(levelname)s: %(message)s'
	formatter = logging.Formatter(log_format)
	logger = gogo.Gogo(
		'examples.fmt',
		low_formatter=formatter,
		high_formatter=formatter).logger

	# Configure our execution type (full-suite vs. single-run):
	execution_type = ExecutionType.ALL if not args['test_number'] else ExecutionType.SINGLE

	# Activate debug mode via command-line flag;
	in_debug_mode = True if args['debug'] else False

	is_valid_folder_structure = check_folder_validity()

	if is_valid_folder_structure:
		if execution_type == ExecutionType.SINGLE:
			test_case_number = args['test_number']

			case_filepath = None

			for path in test_case_filepaths:
				if path.startswith(str(test_case_number) + '_'):
					case_filepath = 'tests/' + path
					break

			if case_filepath:
				with open(case_filepath) as file:
					master_string = file.readline()

				# Strip out any erroneous whitespace from the input:
				master_string = ''.join(master_string.split())

				logger.info(" ------> Executing: " + case_filepath + " <------ ")

				# Check whether the test string given is even valid before starting:
				is_valid_test = check_test_validity()

				if is_valid_test:
					gather_segments(master_string, depth_level, test_bits)
					display_output()
				else:
					logger.info("Test to execute was invalid, skipping.")
			else:
				logger.info("Test case not found, aborting.")
		else:
			for case_filepath in test_case_filepaths:
				with open('tests/' + case_filepath) as file:
					master_string = file.readline()

				# Strip out any erroneous whitespace from the input:
				master_string = ''.join(master_string.split())

				logger.info(" ------> Executing: " + case_filepath + " <------ ")

				# Check whether the test string given is even valid before starting:
				is_valid_test = check_test_validity()

				if is_valid_test:
					gather_segments(master_string, depth_level, test_bits)
					display_output()
				else:
					logger.info("Test to execute was invalid, skipping.")

				reset_state()
	else:
		logger.info("Test case folder is structured incorrectly, aborting.")