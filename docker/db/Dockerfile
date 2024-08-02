FROM postgres:13

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-server-dev-13 \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector extension
RUN git clone --branch v0.4.2 https://github.com/pgvector/pgvector.git /pgvector \
    && cd /pgvector \
    && make \
    && make install

# Set the default command to run PostgreSQL
CMD ["postgres"]
