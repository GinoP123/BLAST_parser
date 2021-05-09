import BLAST_alignments_parser as parser
import os

def last_index(string, char):
	index = None
	for i, ch in enumerate(string[-1::-1]):
		if char == ch:
			index = i
			break
	assert index is not None

	return len(string) - index - 1


def batch(count=0):
	folder_path = input("\tPath to text file folder: ")
	print()

	if not folder_path.endswith("/"):
		folder_path += "/"

	files = []
	for filename in os.listdir(folder_path):
		if filename.endswith(".txt"):
			files.append(filename)

	content = []
	for file in files:
		with open(folder_path + file) as infile:
			content.append(infile.readlines())

	outfile = f"Batch {count}.xlsx"
	parser.parse_batch(files, content, outfile)


def single():
	path = input("\tPath to text file: ")
	assert os.path.exists(path)
	print()

	filename = path
	if "/" in filename:
		filename = filename[last_index(filename, "/")+1:-4]

	with open(path) as infile:
		content = infile.readlines()

	parser.parse(filename, content)



def main():

	batch_count = 0
	while True:
		selection = input("Single or Batch Parse? (s/b) ").strip().lower()
		print()

		if selection == "b" or selection == "s":
			if selection == "b":
				batch_count += 1
				batch(batch_count)
			else:
				single()

			if input("Parse Again? (y/n) ").strip().lower() != "y":
				break
			print()
		else:
			print("ERROR: Invalid Selection\n")

main()