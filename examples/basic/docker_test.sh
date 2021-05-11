#!/usr/bin/env bash

id1=$(docker run -d --ipc="shareable"      oremda/basic_example_loader      /queue0 /queue1 /queue2)
id2=$(docker run -d --ipc="container:$id1" oremda/basic_example_times_two   /queue0 /queue1)
id3=$(docker run -d --ipc="container:$id1" oremda/basic_example_minus_three /queue1 /queue2)
id4=$(docker run -d --ipc="container:$id1" oremda/basic_example_viewer      /queue2)

# Wait for the loader to finish, since it hosts the ipc memory
docker wait $id1

docker logs $id1
docker logs $id2
docker logs $id3
docker logs $id4
