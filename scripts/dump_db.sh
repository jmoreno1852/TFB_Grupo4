#!/usr/bin/env bash
docker run --rm \
  --network container:mongo \
  mongo:7-jammy \
  mongodump --db tfb_database --archive > db_archive/mongo_seed.archive