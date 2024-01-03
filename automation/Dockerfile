FROM jupyter/minimal-notebook

RUN mamba install \
    -c litex-hub \
    -c conda-forge \
    --yes \
    'open_pdks.sky130a' \
    'ngspice' \
    && mamba clean --all -f -y \
    && fix-permissions "${CONDA_DIR}" \
    && fix-permissions "/home/${NB_USER}"

COPY --chown=${NB_UID}:${NB_GID} py_requirements.txt /tmp/
RUN pip install --no-cache-dir --requirement /tmp/py_requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

COPY . .

CMD ["jupyter", "notebook", "--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]