FROM ubuntu:18.04
RUN apt-get update && apt-get install -y python3 python3-pip

ENV WORKDIR   /var/flask_app
RUN mkdir -p $WORKDIR
COPY main.py $WORKDIR
COPY requirements.txt $WORKDIR/
COPY templates/* $WORKDIR/templates/
COPY credential.py $WORKDIR

RUN pip3 install -r $WORKDIR/requirements.txt && python3 -m textblob.download_corpora

#ENV consumer_key=${consumer_key}
#ENV consumer_secret=${consumer_secret}
#ENV access_token=${access_token}
#ENV access_token_secret=${access_token_secret}

ENV FLASK_APP=$WORKDIR/main.py

EXPOSE 8000/tcp
#ENTRYPOINT [""]
CMD ["python3", "/var/flask_app/main.py"]
