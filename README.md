# Dito Challenge API #

This python API is prepared to receive and handle REST requests as specified by the challenge, using a PostgreSQL database. It is run as a microservice that is contained in Docker, prepared to be scaled multiple times, optimized to run N + 1 simultaneous processes in each running container (so concurrency is fine-tuned), where N is the number of cores made available to docker.

## Usage ##

### COLLECTOR API ###

The collector API is served through http://HOST:PORT/ and expects a JSON body containing one or more objects to be saved. The current model is only prepared to receive a timestamp and an event, as was specified by the challenge.

The request body may contain either a single object representing the navigational data to be saved, or an object with a payload property that contains an array of such objects.

e.g: POST request to http://localhost:666 with the following body:
```json
{
	"payload": [
		{
			"event": "raul_seixas",
			"timestamp": "2017-02-27T21:02:14.2133457-03:00"
		},
		{
			"event": "raul_seixas",
			"timestamp": "2018-01-31T04:21:17.3124847-03:00"
		},
		{
			"event": "raulstrophedon",
			"timestamp": "2017-11-03T12:46:42.2311892-03:00"
		}
	]
}
```

### AUTOCOMPLETE ###

You may issue a GET request to [http://HOST:PORT/{query}](http://HOST:PORT/{query}) to search for {query}. The response should be a JSON object that may contain up to two properties: one, `objects`, contains an array with every matching navigation data stored through the POST API; the other, `suggestions`, contains an array that holds matching navigation data events that start with {query}.

Additionally, a GET request to [http://HOST:PORT/{query}/suggestions](http://HOST:PORT/{query}/suggestions) should bring only suggestions, never accessing the database to bring the possibly matched `objects`.

e.g: GET request to http://localhost:666/bu/suggestions

### DATA MANIPULATION ###

While this could easily be a simple function or a separated service, I found it to be more practical for testing reasons to include it together with the previous services. It should be clear that it would be no problem to isolate this service.

The objects are read from the entrypoint and a resulting timeline is returned as specified by the challenge. This parsed result is ordered by timestamp DESC, considering the objects as their represented dates (and not as strings).

It may be run on another endpoints as specified below.

## Running ##

This supposes you have [docker](https://www.docker.com/) and [postgres](https://www.postgresql.org/) installed, and have created an empty database. I also recommend to configure pgsql to allow for free port access to avoid running into any problems of that kind.

You first need to build the docker image. The `build.sh` file facilitates this process, so you just need to run it, optionally specifying a version parameter (that defaults to "latest" if not passed).
e.g.:
```bash
./build.sh 1.2.0
```

Afterwards, you need to run the image, specifying the obligatory environment parameter "DB_URL" and the port on which the API will run. There are optional debugging parameters, namely DEBUG, ECHO, TRACK, and an optional ENDPOINT parameter to specify another endpoint for the data manipulation service to run on (it defaults to the one specified by e-mail).
e.g.:
```bash
#command
docker run -p PORT:80 -e DB_URL=postgresql://user:password@HOST:PORT/DBNAME vihainen-rest:latest
#example
docker run -p 666:80 -e DB_URL=postgresql://postgres:sa@192.168.0.15:5432/dito vihainen-rest:latest
#running on another port and endpoint
docker run -p 6789:80 -e DB_URL=postgresql://postgres:sa@192.168.0.15:5432/dito -e ENDPOINT=https://example.api.endpoint/dito/payload vihainen-rest:latest
```

This should be enough to get it running.
