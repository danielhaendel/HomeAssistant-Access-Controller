FROM python:3.8-slim

RUN pip install paho-mqtt

COPY run.sh /run.sh
COPY user_management.py /user_management.py

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]