# LDO Code a Chip 

[![https://github.com/Mario1159/LDO_CAC/blob/main/automation/ldo.ipynb](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Mario1159/LDO_CAC/blob/main/automation/ldo.ipynb)

> To access the main jupyter in google colab, enable private access in [Colab](https://colab.research.google.com/) > Configuration > Github > Private repository access

Automated generation of an LDO for SKY130

## Usage

Run latest build of the docker image using the command shown below.

```
docker run -d --name ldo_cac_jupyter -p 8888:8888 -e GRANT_SUDO=yes ghcr.io/mario1159/ldo_cac
```

Then open `localhost:8888` in your browser to access the Jupyter notebook.

You can also build the image yourself running the `build` or `all` target in `make`

## How it works

The project provides a script to make an entire LDO based on certain specification or just certains components of it.
This script is executed in detail providing some reports inside the jupyter notebook and can serve as an example to run just the python script.
