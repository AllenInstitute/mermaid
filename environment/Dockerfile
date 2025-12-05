# hash:sha256:49269c823ecf1c75c2f1e5206a461ef2894fe8c8e2c5841493234c45d56162b9
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    mermaid-py==0.8.0 \
    pandas==2.3.3 \
    streamlit==1.52.0 \
    streamlit-mermaid==0.3.0 \
    streamlit-mermaid-interactive==0.1.12

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
