#!/usr/bin/env bash
docker run --rm   --network container:mongo   -i mongo:7   mongorestore --drop --db tfb_database --archive < db_archive/mongo_seed.archive