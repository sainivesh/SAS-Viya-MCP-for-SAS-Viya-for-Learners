## Running with Docker
This repo provides a Dockerfile that can be used to build a docker image for the MCP server. Much more handy for production scenarios, portability, reproducibility, etc.

### Building
Basic:
```sh
# From the repository root 
docker build -t MY_IMG:MY_TAG .
```

You can also pass in the expected host port at build time:
```sh
docker build --build-arg HOST_PORT=8500 -t MY_IMG_ARG:MY_TAG_ARG .
```

### Running
The docker container expects an .env file to be passed in at runtime.

Basic:
```sh
# From the repository root
docker run -d -p 8134:8134 --env-file .env --name YOUR_NAME MY_IMG:MY_TAG
```

If you set a non-default port at build time, make sure you set that in your .env!
```sh
docker run -d -p 8500:8500 --env-file .env --name YOUR_NAME MY_IMG_ARG:MY_TAG_ARG 

# In this case the .env should also have an entry for
HOST_PORT=8500
```
---

Usage is the exact same as when it was run locally.



