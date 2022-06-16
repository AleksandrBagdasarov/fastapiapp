#!/bin/bash

[[ "$DEPLOY" == "" ]] && echo "SET DEPLOY SERVER TYPE" || echo "GOT $DEPLOY SERVER TYPE"



echo $DEPLOY START BUILDING API

docker builder prune -a -f
docker container prune -f

cd deploy
docker-compose -f docker-compose.yml up -d --build redis
docker-compose -f docker-compose.yml up -d --build database
docker-compose -f docker-compose.yml up -d --build nginx
if [[ "$DEPLOY" == "LOCAL" ]]; then
    echo "LOCAL BUILD."
else
    docker-compose -f docker-compose.yml up -d --build app-server
fi


docker ps