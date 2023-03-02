DOCKER_BUILDKIT=1 docker build -t route_planner .
DOCKER_BUILDKIT=1 docker run -p 80:80 -it --rm --name route_planner route_planner
