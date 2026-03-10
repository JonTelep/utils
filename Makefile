.PHONY: help test-csv install-crypto clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test-csv: ## Generate a test CSV (100 rows, quality 0.5)
	cd scripts && python generate_dirty_csv.py 100 0.5

install-crypto: ## Install crypto wallet dependencies
	pip install -r crypto/requirements.txt

clean: ## Remove generated CSV files
	rm -f scripts/dirty_data_*.csv dirty_data_*.csv
