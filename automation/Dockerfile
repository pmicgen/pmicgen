FROM quay.io/jupyter/minimal-notebook

ARG env_name=python311
ARG py_ver=3.11

COPY --chown=${NB_UID}:${NB_GID} automation/environment.yml /tmp/
RUN mamba env create -p "${CONDA_DIR}/envs/${env_name}" -f /tmp/environment.yml && \
     mamba clean --all -f -y

# Disable IPyKernel warning
# https://discourse.jupyter.org/t/what-should-i-do-about-frozen-modules-warning/21528
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

RUN "${CONDA_DIR}/envs/${env_name}/bin/python" -m ipykernel install --user --name="${env_name}" && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

COPY --chown=${NB_UID}:${NB_GID} automation/requirements.txt /tmp/
RUN "${CONDA_DIR}/envs/${env_name}/bin/pip" install --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

USER root
RUN \
    echo conda activate "${env_name}" >> /usr/local/bin/before-notebook.d/10activate-conda-env.sh && \
    echo conda activate "${env_name}" >> /etc/skel/.bashrc && \
    echo conda activate "${env_name}" >> "/home/${NB_USER}/.bashrc"

# TODO: Fix this absolute path
RUN /opt/conda/envs/python311/bin/volare enable $(/opt/conda/envs/python311/bin/volare ls-remote | sed -n '1 p')

# Remove previous default kernel
RUN jupyter kernelspec remove -y python3

COPY . .

# TODO: Non root access (change default user to jovyan)
CMD ["jupyter", "notebook", "--allow-root", "--no-browser", "--NotebookApp.token=''", "--NotebookApp.password=''", "--KernelSpecManager.ensure_native_kernel=False"]