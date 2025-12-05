# hash:sha256:2b89e25ae184131113e6cdc23b2c1efbeec6a267b3fdcf9d29c7f7271708a443
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    pandas==2.3.3 \
    streamlit==1.52.0 \
    streamlit-mermaid==0.3.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
