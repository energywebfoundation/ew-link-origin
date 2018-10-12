FROM python:3.7

# Set our working directory
WORKDIR /usr/src/app

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Remove warnings
ENV PYTHONWARNINGS="ignore"
ENV CONSUMER=''

# bond.py will run when container starts up on the device
CMD ["python","origin-consumer.py"]