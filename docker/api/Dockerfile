# Pull official base image
FROM python:3.12

# Set working directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies including GDAL
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    musl-dev \
    libmagic1 \
    libffi-dev \
    git \
    netcat-traditional \
    gdal-bin libgdal-dev postgresql-client \
    postgis \
    libgeos-dev \
    libproj-dev \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Set up GDAL environment variables
RUN GDAL_SO=$(find /usr/lib -name "libgdal.so.*" | head -n 1) && \
    ln -sf $GDAL_SO /usr/lib/libgdal.so

ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

# Install Dependencies
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN pip install poetry==1.8.2
RUN poetry config virtualenvs.create false
RUN poetry install

# Copy entrypoint.sh
COPY ./docker/api/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY ./app /app

ENTRYPOINT [ "/entrypoint.sh" ]