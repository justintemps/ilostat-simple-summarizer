from . import ilostat, default_area, default_dataflow
from .handlers import init_current_dimensions, handle_get_data_button


class DefaultSettings:
    """
    The DefaultSettings class encapsulates the initialization and configuration
    of data flows, dimensions, and related settings for a specified area
    and dataflow. This class retrieves dataflows, sets up dimensions, and
    prepares relevant data for further processing.

    Attributes:
        _area (str): The area for which dataflows and dimensions are defined.
        dataflow (str): The dataflow associated with the specified area.
        _dataflows (list): A list of available dataflows for the specified area.
        _dimensions (list): Dimensions for the specified area and dataflow.
        _current_dimensions (list): Initialized dimensions set for the current context.
        _data (any): Data retrieved or handled by `handle_get_data_button`.
    """

    def __init__(self, area=default_area, dataflow=default_dataflow):
        """
        Initializes the DefaultSettings object.

        Args:
            area (str, optional): The target area for dataflow retrieval.
                                  Defaults to the imported `default_area`.
            dataflow (str, optional): The target dataflow for the specified area.
                                      Defaults to the imported `default_dataflow`.
        """
        # Private attribute for the area
        self._area = area

        # Dataflow for the specified area
        self._dataflow = dataflow

        # Fetch dataflows associated with the specified area
        self._dataflows = ilostat.get_dataflows(area)

        # Retrieve dimensions for the specified area and dataflow
        self._dimensions = ilostat.get_area_dimensions(area, dataflow)

        # Initialize dimensions for current usage context
        self._current_dimensions = init_current_dimensions(self._dimensions)

        # Handle data retrieval or preparation using a specific handler
        self._data = handle_get_data_button(
            area, dataflow, self._current_dimensions, None, None
        )

    @property
    def area(self):
        """
        Returns the area associated with the current settings.

        Returns:
            str: The area value.
        """
        return self._area

    @property
    def dataflow(self):
        """
        Returns the dataflow associated with the current settings.

        Returns:
            str: The dataflow value.
        """
        return self._dataflow

    @property
    def dataflows(self):
        """
        Returns the list of available dataflows for the specified area.

        Returns:
            list: List of dataflows.
        """
        return self._dataflows

    @property
    def dimensions(self):
        """
        Returns the dimensions for the specified area and dataflow.

        Returns:
            list: List of dimensions.
        """
        return self._dimensions

    @property
    def current_dimensions(self):
        """
        Returns the initialized current dimensions for use in this context.

        Returns:
            list: List of initialized dimensions.
        """
        return self._current_dimensions

    @property
    def data(self):
        """
        Returns the data associated with the current configuration.

        Returns:
            any: The data object handled and retrieved during initialization.
        """
        return self._data


if __name__ == "__main__":
    initial = DefaultSettings()

    print("Initial area", initial.area)
    print("Initial dataflow", initial.dataflow)
    print("Number of dataflows", len(initial.dataflows))
    print("Dimensions", initial.dimensions)
    print("Current dimensions", initial.current_dimensions)
    print("Data", initial.data)
