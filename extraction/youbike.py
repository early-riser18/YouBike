import requests
import pandas as pd
from datetime import datetime
import pytz
from io import StringIO
from utils.env_config import CONFIG
from utils.utils import get_formatted_timestamp_as_str


class YoubikeSnapshot:
    def __init__(self, extraction_ts: datetime, body: str):
        self.extraction_ts = extraction_ts
        self.body = body


def get_youbike_data() -> YoubikeSnapshot:
    """
    Returns the requested data from the youbike endpoint.

        Parameters:
            None -- Endpoint is a constant

        Returns:
            YoubikeSnapshot -- Object containing the requested data
    """

    URL = "https://gcs-youbike2-linebot.microprogram.tw/latest-data/youbike-station.csv"
    r = requests.request("GET", URL)

    tz_tst = pytz.timezone("Asia/Taipei")
    time_now = datetime.today().now(tz=tz_tst)
    data = YoubikeSnapshot(extraction_ts=time_now, body=r.text)
    return data


def basic_preprocessing(data: YoubikeSnapshot) -> YoubikeSnapshot:
    """
    Applies simple preprocessing.

        Parameters:
            data (YoubikeSnapshot) -- The raw snapshot to preprocess

        Returns:
            YoubikeSnapshot -- The preprocessed snapshot
    """

    df = pd.read_csv(StringIO(data.body))
    df["last_update_ts"] = (pd.to_datetime(df["updated_at"], unit="s")
                            .dt.tz_localize(tz='UTC')
                            .dt.tz_convert(tz='Asia/Taipei')
    )
    df.drop(labels=["updated_at"], axis=1, inplace=True)
    data.body = df.to_csv()
    return data


def download_basic_preprocessed_youbike_snapshot() -> str:
    """
    Retrieve Youbike snapshot from endpoint, preprocess it and persist it.

        Parameters:
            None

        Returns:
            str -- path to persisted data
    """
    data = get_youbike_data()
    formatted_ts = get_formatted_timestamp_as_str(data.extraction_ts)
    file_stub = f"youbike_dock_info_{formatted_ts}_raw"
    try:
        preprocessed_data = basic_preprocessing(data)
    except:
        preprocessed_data = data
        file_stup += "error"
        print("An error occured while preprocessing the data")

    file_path = file_stub + ".csv"
    with open(f"./raw_data/{file_path}", "w") as f:
        f.write(preprocessed_data.body)
    return file_path


print("Running module with env:", CONFIG)

if __name__ == "__main__":
    download_basic_preprocessed_youbike_snapshot()