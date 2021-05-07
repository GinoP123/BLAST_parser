import pandas as pd

alignment_line = "Alignments:\n"
strings_to_find = ["Sequence ID: ", "Expect:", "Identities:"]
substrings = ["Identities:", "Positives:", "Gaps:"]
df_columns = ["name", "Genome length",	"E-Value (expect)",	"Percent identities", "Percent positives", "Accession number/Sequence ID"]

phage_data = {}
df_dictionary = {column: [] for column in df_columns}

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


with open(f"{input('BLAST File Name: ')}") as infile:
	data = infile.readlines()

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

names = []
lengths = []

with open(f"names_lengths.txt") as infile_names_lengths:
	lines = infile_names_lengths.readlines()

	for line in lines:
		if not line.strip():
			continue

		name, length = line.strip().split(", ")
		names.append(name)
		lengths.append(length)

		df_dictionary["name"].append(name)
		df_dictionary["Genome length"].append(length)
		for column in df_columns[2:]:
			df_dictionary[column].append("")

	names = [name.strip() for name in names]


with open(f"summary.txt", "w") as outfile:
	outfile.write("Name, Accession, E-Value, % ID, % Positives\n")
	for name in phage_data:
		outfile.write(name + ", " + ", ".join(phage_data[name]) + "\n")


for i, name in enumerate(names):
	if name in phage_data:
		df_dictionary["Accession number/Sequence ID"][i] = phage_data[name][0]
		df_dictionary["E-Value (expect)"][i] = phage_data[name][1]
		df_dictionary["Percent identities"][i] = phage_data[name][2]
		df_dictionary["Percent positives"][i] = phage_data[name][3]

df = pd.DataFrame(df_dictionary)
df.to_excel("BLAST Hits.xlsx", index=False)
