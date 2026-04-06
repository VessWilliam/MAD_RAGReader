FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir streamlit requests python-dotenv

# Copy source code
COPY . .

# Expose port
EXPOSE 8500

CMD ["streamlit", "run", "app.py", "--server.port=8500", "--server.address=0.0.0.0"]