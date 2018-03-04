.PHONY: clean

all:
	make data
	make cv
clean:	
	rm -f stage1_docs/Data/test_data.csv
	rm -f stage1_docs/Data/train_data.csv
data:
	python3 featured_data_generator.py
cv:
	python cross_validation.py
