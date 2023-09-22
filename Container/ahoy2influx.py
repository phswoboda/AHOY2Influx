import requests
import json
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# This class is capable of writing data coming from
# a AHOY-DTU to an Influx-DB. Latter can be used to monitor data e.g. in grafana.

class AHOY2Influx:
    def __init__(self, ahoy_url : str, 
                 influx_url : str, 
                 influx_org : str, 
                 influx_token : str,
                 influx_bucket : str) -> None:
        self.__ahoy_url = ahoy_url;
        self.__influx_url = influx_url;
        self.__influx_org = influx_org;
        self.__influx_token = influx_token;
        self.__influx_bucket = influx_bucket;

        self.__lastInverterData = dict();
        # instantiate influx client
        self.__influx_client = influxdb_client.InfluxDBClient(url=self.__influx_url, 
                                                              token=self.__influx_token, 
                                                              org=self.__influx_org);

        self.__influx_api = self.__influx_client.write_api(write_options=SYNCHRONOUS);

    # this function reads current data from AHOY DTU
    # and writes it to the influx Database in the given bucket
    def update(self) -> dict:
        inverterData = self.__getInverterData();

        if inverterData != False:
             self.__insertDataIntoInflux(inverterData);
    
        return inverterData;

    def __getInverterData(self):

        try:
            result = requests.get(f"{self.__ahoy_url}/api/record/live", timeout=30);
            resultJson = json.loads(result.content);
            self.__lastInverterData = resultJson;
            resultJson = resultJson["inverter"][0];
        except:
            print("AHOY DTU could not be reached!")
            return False
    
        return resultJson;

    def __insertDataIntoInflux(self, inverterData: dict):
        
        try:
            dataPointList = [];

            for data in inverterData:
                point = Point(data["fld"]).tag("unit", data["unit"]).field(data["fld"], float(data["val"]));
                print(point)
                dataPointList.append(point);

            dataPointTuple = tuple(dataPointList);

            self.__influx_api.write(bucket=self.__influx_bucket, 
                                    org=self.__influx_org, 
                                    record=dataPointTuple)
        except:
            print("Access to InfluxDB not possible! Please check credentials!")


if __name__ == "__main__":

    from timeloop import Timeloop
    from datetime import timedelta
    import os

    ahoyUrl = os.getenv("AHOY_URL", default="http://ahoy-dtu");
    influxUrl = os.getenv("INFLUX_URL", default="http://localhost:8086");
    influxOrg = os.getenv("INFLUX_ORG", default="my-org");
    influxToken = os.getenv("INFLUX_TOKEN", default="pv-token");
    influxBucket = os.getenv("INFLUX_BUCKET", default="pv_bucket");
    requestRate = os.getenv("REQUEST_RATE", default="120");

    ahoy2influx = AHOY2Influx(ahoyUrl, 
                              influxUrl,
                              influxOrg,
                              influxToken,
                              influxBucket);

    print(ahoy2influx.update());

    tl = Timeloop()

    @tl.job(interval=timedelta(seconds=requestRate))
    def influxDbUpdate_30s():
        print(ahoy2influx.update())

    tl.start(block=True)
