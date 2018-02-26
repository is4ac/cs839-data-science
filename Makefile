all:
	rm stage1_docs/Data/test_data.csv
	rm stage1_docs/Data/train_data.csv
	python3 featured_data_generator.py
	python pipeline.py
