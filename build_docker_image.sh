#!/bin/bash
docker rm $(docker ps -qa)
docker rmi $(docker images -q)
docker build -t ranishot/psychology_reports_api:latest .
docker image prune --force
#docker run -d ranishot/nubank_api:latest