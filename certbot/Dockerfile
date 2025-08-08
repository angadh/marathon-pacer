FROM certbot/certbot

# Copy the init script
COPY init-cert.sh /init-cert.sh

# Make it executable
RUN chmod +x /init-cert.sh

# Override the default entrypoint
ENTRYPOINT ["/init-cert.sh"]
