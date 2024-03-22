### TL;DR
using redis queue to establish connection between work publisher and worker. Work Publisher publishes work items into redis, Worker picks up (pops) items from the queue

### Architecture Diagram
![architecture_diagram](https://raw.githubusercontent.com/surajn581/redis/main/architecture.jpg)

### Work Publisher
it publishes BlockWorkItem objects to the redis queue named WorkPublisher at the rate of 30 objects per ~100-120 seconds

### Worker
it takes the work_publisher object as input and extracts the details about the redis connection and the queue name. It polls the redis queue that the publisher publishes to. It also uses the publisher object to republish the work items into the queue in case of failure while processing the item so that it can be tried again by the same or different worker.

## Dockerization

### Containerization
the following commands were run to build the docker images:

* `docker build -t worker -f ./worker/Dockerfile .`
* `docker build -t work_publisher -f ./work_publisher/Dockerfile .`

#### Commands to tag and push the images

* `docker tag worker surajn581/worker:1.04`
* `docker push surajn581/worker:1.04`
* `docker tag work_publisher surajn581/work_publisher:1.04`
* `docker push surajn581/work_publisher:1.04`

#### Running the images through docker

1. `docker network create work_network`
2. `docker run --net work_network --name redis -d redis`
3. `docker run --net work_network --name worker -d worker`
4. `docker run --net work_network --name work_publisher -d work_publisher`

we don't use port mapping as all the containers are running in the same network

## Kubernetes
we have deployment files that define the image to be used, the ports to be exposed. Along with deployment we also have service that enable intra-pod communication.

### applying the deployment
1. `kubectl apply -f redis_deployment.yaml`
2. `kubectl apply -f work_publisher_deployment.yaml`
3. `kubectl apply -f worker_deployment.yaml`

### port mapping the redis node port
the node port enables us to access the redis client locally, this can help in debugging
    `kubectl port-forward service/redis 30069:6379`
this will map our localhost's port **30069** to the port **6379** of the service with the name **_redis_** that's attached to the **_redis_** pod

### we can now check the logs of our pods
following commands for fetching logs and sshing into the pod itself
* `k logs worker-f46b9c745-8smvx bash -f`
* `k exec -it worker-f46b9c745-8smvx bash`
