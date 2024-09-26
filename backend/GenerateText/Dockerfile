# Use an official Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Copy the current directory contents into the container
# COPY . /var/task

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}

# Set the file to be executed when the docker container starts
CMD ["app.lambda_handler"]

