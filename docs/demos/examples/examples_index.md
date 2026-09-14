---
hide:
  - toc
tags:
  - Examples
  - DuckDB
  - Spark
---

# Example Notebooks

This section provides a series of examples to help you get started with Splink. You can find the underlying notebooks in the [demos folder](https://github.com/RobinL/splink/tree/master/docs/demos/examples) of the Splink repository.

### :simple-duckdb: DuckDB examples

##### Entity type: Persons

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/deduplicate_50k_synthetic.ipynb">
  Download notebook
</a> [Deduplicating 50,000 records of realistic data based on historical persons](./duckdb/deduplicate_50k_synthetic.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/link_only.ipynb">
  Download notebook
</a> [Using the `link_only` setting to link, but not dedupe, two datasets](./duckdb/link_only.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/real_time_record_linkage.ipynb">
  Download notebook
</a> [Real time record linkage](./duckdb/real_time_record_linkage.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/accuracy_analysis_from_labels_column.ipynb">
  Download notebook
</a> [Accuracy analysis and ROC charts using a ground truth (cluster) column](./duckdb/accuracy_analysis_from_labels_column.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/pairwise_labels.ipynb">
  Download notebook
</a> [Estimating m probabilities from pairwise labels](./duckdb/pairwise_labels.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/deterministic_dedupe.ipynb">
  Download notebook
</a> [Deduplicating 50,000 records with Deterministic Rules](./duckdb/deterministic_dedupe.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/febrl3.ipynb">
  Download notebook [Deduplicating the febrl3 dataset](./duckdb/febrl3.ipynb). Note this dataset comes from [febrl](http://users.cecs.anu.edu.au/~Peter.Christen/Febrl/febrl-0.3/febrldoc-0.3/manual.html), as referenced in A.2 [here](https://arxiv.org/pdf/2008.04443.pdf) and replicated [here](https://recordlinkage.readthedocs.io/en/latest/ref-datasets.html).
</a>

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/febrl4.ipynb">
  Download notebook [Linking the febrl4 datasets](./duckdb/febrl4.ipynb). As above, these datasets are from [febrl](http://users.cecs.anu.edu.au/~Peter.Christen/Febrl/febrl-0.3/febrldoc-0.3/manual.html), replicated [here](https://recordlinkage.readthedocs.io/en/latest/ref-datasets.html).
</a>

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb_no_test/cookbook.ipynb">
  Download notebook
</a> [Cookbook of various Splink techniques](./duckdb_no_test/cookbook.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb_no_test/comparison_playground.ipynb">
  Download notebook
</a> [Interactive comparison playground](./duckdb_no_test/comparison_playground.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb_no_test/bias_eval.ipynb">
  Download notebook
</a> [Investigating Bias in a Splink Model](./duckdb_no_test/bias_eval.ipynb)

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb_no_test/pseudopeople-acs.ipynb">
  Download notebook [Linking the pseudopeople Census and ACS datasets](./duckdb_no_test/pseudopeople-acs.ipynb). These datasets are generated using [pseudopeople](https://pseudopeople.readthedocs.io/en/latest/).
</a>


##### Entity type: Financial transactions

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb/transactions.ipynb">
  Download notebook
</a> [Linking financial transactions](./duckdb/transactions.ipynb)

##### Entity type: Businesses

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/duckdb_no_test/business_rates_match.ipynb">
  Download notebook
</a> [Matching business rates data with Companies House data](./duckdb_no_test/business_rates_match.ipynb)


### :simple-apachespark: PySpark examples

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/spark/deduplicate_1k_synthetic.ipynb">
  Download notebook
</a> [Deduplication of a small dataset using PySpark. Entity type is persons.](./spark/deduplicate_1k_synthetic.ipynb)

### :simple-sqlite: SQLite examples

<a target="_blank" href="https://robinl.github.io/splink/demos/examples/sqlite/deduplicate_50k_synthetic.ipynb">
  Download notebook
</a> [Deduplicating 50,000 records of realistic data based on historical persons](./sqlite/deduplicate_50k_synthetic.ipynb)
