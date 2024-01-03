all: clean build run

# TODO: Replace ignore for containter finder
clean:
	-docker stop ldo_cac_jupyter
	-docker rm ldo_cac_jupyter

build:
	docker build -t ldo_cac automation

run:
	docker run -d --name ldo_cac_jupyter -p 8888:8888 --user root -e GRANT_SUDO=yes ldo_cac