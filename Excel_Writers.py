import os
import pandas as pd
import numpy as np

df_columns = ["name", "Genome length",	"E-Value (expect)",	"Percent identities", "Percent positives", "Accession number/Sequence ID"]

phage_names = []
phage_lengths = []

with open(f"names_lengths.txt") as infile_names_lengths:
	lines = infile_names_lengths.readlines()

	for line in lines:
		if not line.strip():
			continue

		name, length = line.strip().split(", ")
		phage_names.append(name)
		phage_lengths.append(length)

assert len(phage_names) == 96


def format_columns(writer, sheet_name, df):
	workbook = writer.book
	worksheet = writer.sheets[sheet_name]

	for i, col in enumerate(df.columns):
	    max_width = max(df[col].astype(str).str.len())
	    max_width = max(max_width, len(col)) + 2
	    worksheet.set_column(i, i, max_width)


class Excel_Writer:
	def __init__(self, path):
		self.path = path

	def write(self, filename, phage_data):
		df_dictionary = {column: [] for column in df_columns}

		for name, length in zip(phage_names, phage_lengths):
			df_dictionary["name"].append(name)
			df_dictionary["Genome length"].append(length)
			for column in df_columns[2:]:
				df_dictionary[column].append("")
		names = [name.strip() for name in phage_names]

		for i, name in enumerate(names):
			if name in phage_data:
				df_dictionary["Accession number/Sequence ID"][i] = phage_data[name][0]
				df_dictionary["E-Value (expect)"][i] = phage_data[name][1]
				df_dictionary["Percent identities"][i] = phage_data[name][2]
				df_dictionary["Percent positives"][i] = phage_data[name][3]


		if os.path.exists(self.path):
			os.remove(self.path)

		df = pd.DataFrame(df_dictionary)
		df.to_excel(self.path, index=False)

		assert len(df) == 96
		assert os.path.exists(self.path)



class Excel_Batch_Writer:
	def __init__(self, path):
		self.path = path

	def write(self, filenames, batch_phage_data):

		columns = ["name"] + filenames
		sheets = ["Sequence IDs", "E-Values", "Percent IDs", "Percent positives"]

		data_lists = [[phage_names] for _ in range(4)]


		for filename in filenames:
			phage_data = batch_phage_data[filename]
			data_matrix = [phage_data[phage_name] if phage_name in phage_data else [""] * 4 for phage_name in phage_names]
			
			lists = map(lambda x: list(x), zip(*data_matrix))
			for data_list, new_list in zip(data_lists, lists):
				data_list.append(new_list)

		data_arrays = [np.array(data_list) for data_list in data_lists]

		if os.path.exists(self.path):
			os.remove(self.path)

		writer = pd.ExcelWriter(self.path, engine='xlsxwriter')
		for sheet_name, data_array in zip(sheets, data_arrays):
			
			df_dictionary = {}
			for column, arr in zip(columns, data_array):
				df_dictionary[column] = arr
				assert len(arr) == len(data_array[0])

			df = pd.DataFrame(df_dictionary)
			df.to_excel(writer, sheet_name, index=False, startrow=1)

			format_columns(writer, sheet_name, df)

		writer.save()

		assert os.path.exists(self.path)

