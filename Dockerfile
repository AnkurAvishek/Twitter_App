FROM ubuntu:18.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
   
RUN mkdir -p ~/flask_app
RUN cd ~/flask_app/
COPY requirement.txt ~/flask_app/
RUN python3 -m venv ~/flask_app/env
RUN source bin/activate
RUN pip3 install -r requirements.txt
RUN python -m textblob.download_corpora
COPY main.py ~/flask_app/
COPY ./templates/* ~/flask_app/templates/
EXPOSE 8000
COPY main.py .
CMD ["python3", "~/flask_app/main.py"]
