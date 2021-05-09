import Excel_Writers as Excel_Writers

alignment_line = "Alignments:\n"
strings_to_find = ["Sequence ID: ", "Expect:", "Identities:"]
substrings = ["Identities:", "Positives:", "Gaps:"]


def find_text(String, char1, char2):
	return String[String.index(char1)+1: String.index(char2)]

def parse_line(String, line_type):
	if line_type == 0:
		data = [String.lstrip(strings_to_find[0]).split(" ")[0]]
	elif line_type == 1:
		data = [String.split(strings_to_find[1])[1].rstrip(", \n")]
	else:
		data = String.split(", ")
		data[-1] = data[-1].rstrip("\n")
		data = [info.lstrip(substrings[i]) for i, info in enumerate(data)]
		data = ["{:.2%}".format(eval(info[:info.index("(")])) for info in data]
		data = data[:-1]
	return data


def parse(filename, data, write=True, path=None):
	if path is None and filename:
		path = f"{filename}.xlsx"

	phage_data = {}

	new_list = []
	found_alignment_section = False
	for line in data:
		if line == alignment_line:
			found_alignment_section = True

		if ">" in line and found_alignment_section:
			if line.index(">") != 0:
				lines = line.split(">")	
				assert len(lines) == 2		
				lines[-1] = ">" + lines[-1]
				new_list.extend(lines)
				continue
		new_list.append(line)
	data = new_list


	names = []
	for line in data:
		if ">" in line:
			names.append(find_text(line, "[", "]"))
			if names[-1] not in phage_data:
				phage_data[names[-1]] = []
			else:
				names.pop()
		elif names:
			if len(phage_data[names[-1]]) == 0:
				if strings_to_find[0] in line:
					phage_data[names[-1]].extend(parse_line(line, 0))

			elif strings_to_find[len(phage_data[names[-1]])] in line:
				info = parse_line(line, len(phage_data[names[-1]]))
				for name in names:
					phage_data[name].extend(info)

				if len(phage_data[names[-1]]) == 4:
					names = []

	for name in phage_data:
		assert len(phage_data[name]) == 4

	if write:
		single_writer = Excel_Writers.Excel_Writer(path)
		single_writer.write(filename, phage_data)

	return phage_data


def parse_batch(filenames, content_lists, path="Batch.xlsx"):
	# return " ".join(filenames)

	batch_phage_data = {}

	for filename, content in zip(filenames, content_lists):
		batch_phage_data[filename] = parse(None, content, False)

	batch_writer = Excel_Writers.Excel_Batch_Writer(path)
	batch_writer.write(filenames, batch_phage_data)

