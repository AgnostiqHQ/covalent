# Covalent Queuer Service API

## Getting started

You must run NATS MQ in order to run the server:

```shell
docker pull nats:latest
docker run -p 4222:4222 -ti nats:latest
```

To run the server you can run
```shell
python main.py
```

You can access the API docs at [http://localhost:8000/docs](http://localhost:8000/docs)
