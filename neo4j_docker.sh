docker run \
    --detach \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/cogch_neo4j/data:/data \
    --volume=$HOME/cogch_neo4j/logs:/logs \
    neo4j:3.1