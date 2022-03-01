from splink.duckdb.duckdb_linker import DuckDBInMemoryLinker
from try_settings import settings_dict
import pandas as pd


from try_settings import settings_dict


df = pd.read_csv("./tests/datasets/fake_1000_from_splink_demos.csv")


linker = DuckDBInMemoryLinker(settings_dict, input_tables={"fake_data_1": df})


linker.train_u_using_random_sampling(target_rows=1e6)


blocking_rule = "l.first_name = r.first_name and l.surname = r.surname"
linker.train_m_using_expectation_maximisation(blocking_rule)


blocking_rule = "l.dob = r.dob"
linker.train_m_using_expectation_maximisation(blocking_rule)

df = linker.predict()

df_pd = df.as_pandas_dataframe()
df_pd.sort_values(["unique_id_l", "unique_id_r"]).head(20)
linker.settings_obj.match_weights_chart()