FROM python:alpine3.18

RUN apk add python3 curl

ADD ahoy2influx.py /usr/share/pvMonitor/ahoy2influx.py

RUN chmod ugo+rwx /usr/share/pvMonitor
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install timeloop influxdb-client requests

ENV AHOY_URL=http://ahoy-dtu
ENV INFLUX_URL=http://localhost:8086
ENV INFLUX_TOKEN=pv_token
ENV INFLUX_BUCKET=pv_bucket
ENV INFLUX_ORG=pv-org

WORKDIR /usr/share/pvMonitor

CMD ["python3", "ahoy2influx.py"]

# documentation
# EXPOSE 80 

#CMD ["nginx", "-g", "daemon off;"]

