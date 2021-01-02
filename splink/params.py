from copy import deepcopy
import os
import json

from pyspark.sql.session import SparkSession

from .settings import Settings, complete_settings_dict
from .charts import (
    load_chart_definition,
    altair_if_installed_else_json,
    _load_multi_chart_template,
    _load_external_libs,
    _make_json,
)

import logging

logger = logging.getLogger(__name__)


class Params:
    """Stores the current model parameters (in self.params) and values for params for all previous iterations

    Attributes:
        params (str): A dictionary storing the current parameters.

    """

    def __init__(self, settings: dict, spark: SparkSession):
        """

        Args:
            settings (dict): A splink setting dictionary
            spark (SparkSession): Your sparksession. Defaults to None.
        """

        self.param_history = []

        self.iteration = 0

        # Settings is just a wrapper around the settings dict
        settings_dict_original = deepcopy(settings)
        self.settings_original = Settings(settings_dict_original)

        settings_dict_completed = complete_settings_dict(deepcopy(settings), spark)

        self.params = Settings(deepcopy(settings_dict_completed))

        self.log_likelihood_exists = False

    def _populate_params_from_maximisation_step(self, lambda_value, pi_df_collected):
        """
        Take results of sql query that computes updated values
        and update parameters.

        df_pi_collected is like
        gamma_value, new_probability_match, new_probability_non_match, gamma_col
        """

        self.params.reset_all_probabilities()

        self.params["proportion_of_matches"] = lambda_value
        for row_dict in pi_df_collected:
            name = row_dict["column_name"]
            level_int = row_dict["gamma_value"]
            match_prob = row_dict["new_probability_match"]
            non_match_prob = row_dict["new_probability_non_match"]

            self.params.set_m_probability(name, level_int, match_prob, force=False)
            self.params.set_u_probability(name, level_int, non_match_prob, force=False)

    def is_converged(self):
        p_latest = self.params
        p_previous = self.param_history[-1]
        threshold = self.params["em_convergence"]

        diffs = []

        change_lambda = abs(
            p_latest["proportion_of_matches"] - p_previous["proportion_of_matches"]
        )
        diffs.append(
            {"col_name": "proportion_of_matches", "diff": change_lambda, "level": ""}
        )

        compare = zip(p_latest.comparison_columns, p_previous.comparison_columns)
        for c_latest, c_previous in compare:
            for m_or_u in ["m_probabilities", "u_probabilities"]:
                for gamma_index in range(c_latest.num_levels):
                    val_latest = c_latest[m_or_u][gamma_index]
                    val_previous = c_previous[m_or_u][gamma_index]
                    diff = abs(val_latest - val_previous)
                    diffs.append(
                        {"col_name": c_latest.name, "diff": diff, "level": gamma_index}
                    )

        diffs = sorted(diffs, key=lambda x: x["diff"], reverse=True)
        largest_diff = diffs[0]["diff"]
        largest_diff_name = diffs[0]["col_name"]
        largest_diff_level = diffs[0]["level"]

        if largest_diff_level != "":
            level_info = f", level {largest_diff_level}"
        else:
            level_info = ""
        logger.info(
            f"The maximum change in parameters was {largest_diff} for key {largest_diff_name}{level_info}"
        )

        return largest_diff < threshold

    def save_params_to_iteration_history(self):
        """
        Take current params and
        """
        current_params = deepcopy(self.params.settings_dict)

        self.param_history.append(Settings(current_params))
        if "log_likelihood" in self.params.settings_dict:
            self.log_likelihood_exists = True

    def _to_dict(self):
        p_dict = {}
        p_dict["current_params"] = self.params.settings_dict
        p_dict["historical_params"] = [s.settings_dict for s in self.param_history]
        p_dict["settings_original"] = self.settings_original.settings_dict
        p_dict["iteration"] = self.iteration

        return p_dict

    def save_params_to_json_file(self, path, overwrite=False):

        if os.path.isfile(path) and not overwrite:
            raise ValueError(
                f"The path {path} already exists. Please provide a different path."
            )

        d = self._to_dict()
        with open(path, "w") as f:
            json.dump(d, f, indent=4)

    #######################################################################################
    # The rest of this module is just 'presentational' elements - charts, and __repr__ etc.
    #######################################################################################

    def m_u_history_as_rows(self):
        rows = []
        for it_num, p in enumerate(self.param_history):
            new_rows = p.m_u_as_rows()
            for r in new_rows:
                r["iteration"] = it_num
                r["final"] = it_num == self.iteration

            rows.extend(new_rows)
        return rows

    def lambda_history_as_rows(self):
        rows = []
        for it_num, p in enumerate(self.param_history):
            rows.append({"λ": p["proportion_of_matches"], "iteration": it_num})

        return rows

    def ll_history_as_rows(self):

        rows = []
        for it_num, p in enumerate(self.param_history):
            rows.append({"log_likelihood": p["log_likelihood"], "iteration": it_num})

        return rows

    def lambda_iteration_chart(self):  # pragma: no cover
        chart_path = "lambda_iteration_chart_def.json"
        chart = load_chart_definition(chart_path)
        chart["data"]["values"] = self.lambda_history_as_rows()
        return altair_if_installed_else_json(chart)

    def ll_iteration_chart(self):  # pragma: no cover
        if self.log_likelihood_exists:
            chart_path = "ll_iteration_chart_def.json"
            chart = load_chart_definition(chart_path)
            chart["data"]["values"] = self.ll_history_as_rows()
            return altair_if_installed_else_json(chart)
        else:
            raise Exception(
                "Log likelihood not calculated.  To calculate pass 'compute_ll=True' to get_scored_comparisons(). Note this causes algorithm to run more slowly because additional calculations are required."
            )

    def gamma_distribution_chart(self):  # pragma: no cover
        chart_path = "gamma_distribution_chart_def.json"
        chart = load_chart_definition(chart_path)
        chart["data"]["values"] = self.params.m_u_as_rows()
        return altair_if_installed_else_json(chart)

    def bayes_factor_chart(self):
        return self.params.bayes_factor_chart()

    def probability_distribution_chart(self):
        return self.params.probability_distribution_chart()

    def bayes_factor_history_charts(self):
        chart_path = "bayes_factor_history_chart_def.json"
        chart_template = load_chart_definition(chart_path)

        # Empty list of chart definitions
        chart_defs = []

        # Full iteration history
        data = self.m_u_history_as_rows()

        # Create charts for each column
        for cc in self.params.comparison_columns:

            chart_def = deepcopy(chart_template)

            # Assign iteration history to values of chart_def
            chart_def["data"]["values"] = [
                d for d in data if d["column_name"] == cc.name
            ]
            chart_def["title"]["text"] = cc.name
            chart_def["hconcat"][1]["layer"][0]["encoding"]["color"]["legend"][
                "tickCount"
            ] = (cc.num_levels - 1)
            chart_defs.append(chart_def)

        combined_charts = {
            "config": {
                "view": {"width": 400, "height": 120},
            },
            "title": {"text": "Bayes factor iteration history", "anchor": "middle"},
            "vconcat": chart_defs,
            "resolve": {"scale": {"color": "independent"}},
            "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        }

        return altair_if_installed_else_json(combined_charts)

    def m_u_probabilities_iteration_chart(self):  # pragma: no cover
        chart_path = "m_u_iteration_chart_def.json"
        chart = load_chart_definition(chart_path)
        chart["data"]["values"] = self.m_u_history_as_rows()
        return altair_if_installed_else_json(chart)

    def all_charts_write_html_file(
        self, filename="splink_charts.html", overwrite=False
    ):

        if os.path.isfile(filename) and not overwrite:
            raise ValueError(
                f"The path {filename} already exists. Please provide a different path."
            )

        template = _load_multi_chart_template()
        fmt_dict = _load_external_libs()

        fmt_dict["c_prob_dist"] = _make_json(self.probability_distribution_chart())
        fmt_dict["c_bayes_factor"] = _make_json(self.bayes_factor_chart())
        fmt_dict["c_gamma_dist"] = _make_json(self.gamma_distribution_chart())
        fmt_dict["c_lambda_it"] = _make_json(self.lambda_iteration_chart())
        fmt_dict["c_bayes_factor_hist"] = _make_json(self.bayes_factor_history_charts())
        fmt_dict["c_m_u_hist"] = _make_json(self.m_u_probabilities_iteration_chart())
        fmt_dict["proportion_of_matches"] = self.params["proportion_of_matches"]
        with open(filename, "w") as f:
            f.write(template.format(**fmt_dict))

    def __repr__(self):  # pragma: no cover
        p = self.params
        return p.__repr__()


def load_params_from_json(path):
    # Load params
    with open(path, "r") as f:
        params_from_json = json.load(f)

    p = load_params_from_dict(params_from_json)

    return p


def load_params_from_dict(param_dict):

    keys = set(param_dict.keys())

    expected_keys = {
        "current_params",
        "settings_original",
        "historical_params",
        "iteration",
    }

    if keys == expected_keys:
        p = Params(param_dict["current_params"], spark=None)

        p.param_history = [Settings(p) for p in param_dict["historical_params"]]
        p.settings_original = Settings(param_dict["settings_original"])
        p.iteration = param_dict["iteration"]
    else:
        raise ValueError("Your saved params seem to be corrupted")

    return p
