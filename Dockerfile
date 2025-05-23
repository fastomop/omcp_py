FROM denoland/deno:latest

WORKDIR /app

# Copy runner.js into the container
COPY runner.js ./runner.js

# Create a directory for node_modules
RUN mkdir -p /app/node_modules
RUN chmod 777 /app/node_modules

# Expose port 8000 (if required by your integration)
EXPOSE 8000

# Updated CMD: Run the runner.js script with restricted read permissions and memory limits.
# Adjust the --allow-read flag with additional paths if necessary for Pyodide assets.
CMD ["deno", "run", "--allow-read=runner.js,/app/pyodide_data", "--v8-flags=--max-heap-size=20", "runner.js"]