# docker-cloud-cli
==================

## Installation

In order to install the Docker Cloud CLI, you can use pip install:

	pip install docker-cloud

For Mac OS users, you can use brew install:

	brew install docker-cloud

Now you can start using it:

     usage: docker-cloud [-h] [-v]
                        {action,container,event,exec,login,node,nodecluster,repository,run,service,stack,tag,trigger,up}
                        ...
    
    Docker Cloud CLI
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
    
    Docker Cloud CLI commands:
      {action,container,event,exec,login,node,nodecluster,repository,run,service,stack,tag,trigger,up}
        action              Action-related operations
        container           Container-related operations
        event               Get real time Docker Cloud events
        exec                Run a command in a running container
        login               Please use "docker login" to log into Docker Cloud
        node                Node-related operations
        nodecluster         NodeCluster-related operations
        repository          Repository-related operations
        run                 Create and run a new service
        service             Service-related operations
        stack               Stack-related operations
        tag                 Tag-related operations
        trigger             Trigger-related operations
        up                  Create and deploy a stack

## Docker image

You can also install the CLI via Docker:

    docker run dockercloud/cli -h

You will have to pass your username and password as environment variables, as the credentials in the image will not persist by default:

    docker run -it -e DOCKERCLOUD_USER=username -e DOCKERCLOUD_PASS=password dockercloud/cli

To make things easier, you might want to use an alias for it:

    alias docker-cloud="docker run -it -e DOCKERCLOUD_USER=username -e DOCKERCLOUD_PASS=password --rm dockercloud/cli"

or

    alias docker-cloud="docker run -it -v ~/.docker:/root/.docker:ro --rm dockercloud/cli"

Then, you can run commands like:

    docker-cloud service
    docker-cloud exec

## Authentication

In order to manage your apps and containers running on Docker Cloud, you need to log into Docker in any of the following ways (will be used in this order):

* Login using Docker CLI:

        $ docker login
        Username: admin
        Password:
        Login succeeded!

* Set the environment variables `DOCKERCLOUD_USER`, `DOCKERCLOUD_PASS`:

        export DOCKERCLOUD_USER=<username>
        export DOCKERCLOUD_PASS=<password>

* Set the environment variables `DOCKERCLOUD_AUTH`:

`DOCKERCLOUD_AUTH` is the environment variable injected via API roles

_Note: docker-cloud CLI and python-dockercloud will pick up the auth in the following order:_

* DOCKERCLOUD_AUTH
* DOCKERCLOUD_USER, DOCKERCLOUD_APIKEY
* DOCKERCLOUD_USER, DOCKERCLOUD_PASS
* ~/.docker/config.json
