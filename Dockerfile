# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Update all packages 
RUN apt-get update

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy and run the requirements.txt file to install the required packages.
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy files from the current directory to the image's filesystem
COPY Populate_database_script.py config.py ./

# Execute the script in the container
CMD ["python", "Populate_database_script.py"]