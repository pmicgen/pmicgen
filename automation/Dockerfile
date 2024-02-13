FROM jupyter/minimal-notebook

ARG env_name=pyicenv
ARG py_ver=3.10

USER root
RUN apt update -y
RUN apt upgrade -y

# Add sudo rights to jovyan
RUN usermod -aG sudo jovyan
RUN echo "jovyan ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/jovyan-nopasswd

USER jovyan
ENV PATH="/home/jovyan/.local/bin:${PATH}"

COPY --chown=${NB_UID}:${NB_GID} automation/environment.yml /tmp/
RUN mamba env create -p "${CONDA_DIR}/envs/${env_name}" -f /tmp/environment.yml && \
     mamba clean --all -f -y

# Disable IPyKernel warning
# https://discourse.jupyter.org/t/what-should-i-do-about-frozen-modules-warning/21528
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

RUN "${CONDA_DIR}/envs/${env_name}/bin/python" -m ipykernel install --user --name="${env_name}" --display-name "Python IC Development" && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

COPY --chown=${NB_UID}:${NB_GID} automation/requirements.txt /tmp/
RUN "${CONDA_DIR}/envs/${env_name}/bin/pip" install --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

USER root
# TODO: For some reason vscode is not detecting the kernel, can be a path issue
RUN \
    echo conda activate "${env_name}" >> /usr/local/bin/before-notebook.d/10activate-conda-env.sh && \
    echo conda activate "${env_name}" >> /etc/skel/.bashrc && \
    echo conda activate "${env_name}" >> "/home/${NB_USER}/.bashrc"

# Remove previous default kernel
RUN jupyter kernelspec remove -y python3

USER jovyan
RUN "/opt/conda/envs/${env_name}/bin/volare" enable $("/opt/conda/envs/${env_name}/bin/volare" ls-remote | sed -n '1 p')

COPY --chown=jovyan:users . .

RUN chmod +x "/home/jovyan/automation/docker/cmd.sh"
CMD ["/home/jovyan/automation/docker/cmd.sh"]