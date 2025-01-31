import gradio as gr
from ilostat.ilostat import ILOStat
from . import ilostat, CHATBOT_MODEL
from ._dim_controller import DimensionController
from predict.chat import ChatBot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Generator, Any, Tuple

# Set pandas options to avoid silent downcasting warnings when dealing with data types
pd.set_option("future.no_silent_downcasting", True)


class AppController:
    """
    The AppController class handles interactions with ILOSTAT data
    and creates components for a user interface using Gradio.
    It enables data querying, formatting, and visualization based on
    user-selected parameters such as area and dataflows.
    """

    def __init__(self, ilostat: ILOStat = ilostat):
        """
        Initialize the AppController with an ILOStat instance.

        Parameters:
        - ilostat (ILOSTAT): The ILOSTAT instance for querying and retrieving data.
        """
        self._ilostat = ilostat
        self.dimension_controller = DimensionController
        self._chatbot = ChatBot(model=CHATBOT_MODEL)

    def set_dataflows(self, area: str):
        """
        Set and populate the dataflow dropdown based on the selected area.

        Parameters:
        - area (str): The selected geographic area.

        Returns:
        - gr.Dropdown: A Gradio dropdown populated with dataflows for the selected area.
        - None: If no area is selected.
        """
        if area:
            dataflows = self._ilostat.get_dataflows(area)
            return gr.Dropdown(choices=dataflows)
        return None

    def set_description(self, dataflow: str):
        """
        Retrieve and set the description for a given dataflow.

        Parameters:
        - dataflow (str): The dataflow for which to retrieve the description.

        Returns:
        - str: The description of the dataflow.
        """
        description = self._ilostat.get_dataflow_description(dataflow)
        return description

    def set_dimensions(self, area: str, dataflow: str):
        """
        Retrieve and set dimensions for a given area and dataflow.

        Parameters:
        - area (str): The selected geographic area.
        - dataflow (str): The selected dataflow.

        Returns:
        - list: List of dimensions for the specified area and dataflow.
        - None: If no dataflow is provided.
        """
        if dataflow:
            dimensions = self._ilostat.get_area_dimensions(area=area, dataflow=dataflow)
            return dimensions
        return None

    def init_current_dimensions(self, dimensions):
        """
        Initialize current dimensions with default values.

        Parameters:
        - dimensions (list): List of dimension dictionaries, each containing keys
          'dimension' and 'values'.

        Returns:
        - dict: A dictionary mapping dimension names to their default values.
        """
        current_dimensions = {}
        for dim in dimensions:
            key = dim["dimension"][0]  # Extract dimension key
            val = dim["values"][0][1]  # Extract default value
            current_dimensions[key] = val
        return current_dimensions

    def set_dataframe(
        self,
        area: str,
        dataflow: str,
        dimensions: dict[str, str],
        start_period: str,
        end_period: str,
    ):
        """
        Retrieve data as a DataFrame based on user-selected parameters.

        Parameters:
        - area (str): The selected geographic area.
        - dataflow (str): The selected dataflow.
        - dimensions (dict): A dictionary mapping dimension keys to their values.
        - start_period (str): The start period for data retrieval.
        - end_period (str): The end period for data retrieval.

        Returns:
        - pd.DataFrame: Data retrieved based on the provided parameters.
        """
        # Filter out keys with null or empty values from dimensions
        dimensions = {key: value for key, value in dimensions.items() if value}

        # Include the area if it's provided
        if area:
            dimensions["REF_AREA"] = area

        # Create query parameters excluding null values
        params = {
            key: value
            for key, value in {
                "startPeriod": start_period,
                "endPeriod": end_period,
            }.items()
            if value
        }

        # Execute the query with the specified parameters
        query = self._ilostat.query(
            dataflow=dataflow, dimensions=dimensions, params=params
        )
        result = query.data()

        return result.dataframe

    def render_chart(self, df: pd.DataFrame):
        """
        Generate a chart based on a given DataFrame.

        Parameters:
        - df (pd.DataFrame): The data to be visualized.

        Returns:
        - gr.Plot: A Gradio plot object displaying the data.
        """

        if "value" in df.columns:
            # Replace empty strings with NaN for consistency
            df["value"] = df["value"].replace("", np.nan, regex=False)
            fig = plt.figure()

            # Set axis labels
            plt.xlabel("Time period")

            # Group and plot data based on classification columns
            classifications = [col for col in df.columns if "classif" in col.lower()]
            for classification in classifications:
                for group_name, group_df in df.groupby(classification):
                    plt.plot(
                        group_df["TIME_PERIOD"], group_df["value"], label=group_name
                    )

            # Adjust layout for readability
            fig.autofmt_xdate()

            # Create the plot object before closing the figure
            plot = gr.Plot(value=fig)

            # Close the figure to free up memory
            plt.close(fig)

            return plot

    def set_chart(self, df: pd.DataFrame):
        # Create a copy of the DataFrame to avoid mutating the original
        df_copy = df.copy()
        return self.render_chart(df_copy)

    def set_prompt(self, area: str, dataflow: str, df: pd.DataFrame):

        # Get the dataflow label
        data_label = ilostat.get_dataflow_label(dataflow)

        # Get the area label
        area_label = ilostat.get_area_label(area)

        # Get a response from the chatbot
        prompt = self._chatbot.prompt(df, area_label, data_label, dataflow)

        return prompt

    def chat_completion(self, prompt: str) -> Generator[str | Any, Any, None]:
        # Get a response from the chatbot
        for response in self._chatbot.respond(prompt):
            yield response


if __name__ == "__main__":
    from app.defaults import AppDefaults

    initial = AppDefaults()

    controller = AppController()

    initial_dimensions = controller.set_dimensions(initial.area, initial.dataflow)

    current_dimensions = controller.init_current_dimensions(initial.dimensions)

    print(initial_dimensions)
