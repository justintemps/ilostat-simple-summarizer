import sdmx
import pandas as pd


class ILOStatQuery:
    def __init__(
        self,
        dataflow: str,
        dimensions: dict[str, str],
        params: dict[str, str],
    ):
        self.dataflow = dataflow
        self.dimensions = dimensions
        self.params = params
        self._ilostat = sdmx.Client("ILO")

        self._dsd = None
        self._set_dsd()

    def _set_dsd(self):
        # Get the dataflow message
        df_msg = self._ilostat.dataflow(self.dataflow)

        # Get the dataflow structure
        df_flow = df_msg.dataflow[self.dataflow]

        # Get the DSD
        self._dsd = df_flow.structure

    def data(self):
        # Get the dataflow message
        data_msg = self._ilostat.data(
            self.dataflow,
            dsd=self._dsd,
            key=self.dimensions,
            params=self.params,
        )

        data = data_msg.data[0]

        series_data = sdmx.to_pandas(data)

        df = series_data.reset_index(name="value")

        return df


if __name__ == "__main__":
    df = "DF_UNE_TUNE_SEX_MTS_DSB_NB"

    dimensions = {
        "FREQ": "A",
        "MEASURE": "UNE_TUNE_NB",
        "SEX": "SEX_T",
        "MTS": "MTS_DETAILS_MRD",
        "DSB": "DSB_STATUS_NODIS",
        "REF_AREA": "ITA",
    }

    params = {"startPeriod": "2015"}

    query = ILOStatQuery(
        dataflow="DF_UNE_TUNE_SEX_MTS_DSB_NB", dimensions=dimensions, params=params
    )

    result = query.data()

    print(type(result))

    print(result)
