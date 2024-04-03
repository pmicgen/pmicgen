all: clean build run

.PHONY: all build

clean:
	-docker rm -f ldo_cac_jupyter

build:
	docker build -t pmicgen_jupyter -f docker/Dockerfile .

run:
	docker run -d --name pmicgen_jupyter -p 8888:8888 -e GRANT_SUDO=yes ldo_cac

remote-run:
	@if [ -z "$GITHUB_PAT" ]; then\
		echo "Environment variable GITHUB_PAT does not exists"\
	fi
	@if [ -z "$GITHUB_USER" ]; then\
		echo "Environment variable GITHUB_USER does not exists"\
	fi
	echo $GITHUB_PAT | docker login ghcr.io --username $GITHUB_USER --password-stdin\