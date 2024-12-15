FROM nginx:alpine

# Create log directory
RUN mkdir -p /var/log/nginx

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy static files
COPY ./static /usr/share/nginx/html/static
COPY ./assets /usr/share/nginx/html/assets
COPY index.html /usr/share/nginx/html/

# Copy nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Forward nginx logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

CMD ["nginx", "-g", "daemon off;"]
