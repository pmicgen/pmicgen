all: clean build run

clean:
	@if [ "$$(docker inspect -f '{{.State.Running}}' ldo_cac_jupyter)" == "true" ]; then\
		docker stop ldo_cac_jupyter;\
		docker rm ldo_cac_jupyter;\
	fi

build:
	docker build -f automation/Dockerfile -t ldo_cac .

run:
	docker run -d --name ldo_cac_jupyter -p 8888:8888 --user root -e GRANT_SUDO=yes ldo_cac