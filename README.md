# CapstoneProject

CapstoneProject
Description
CapstoneProject is a cutting-edge Python project focused on enhancing language translation capabilities. It leverages the LibreTranslate API and employs a RabbitMQ server to ensure efficient and reliable message queuing. This setup is ideal for applications requiring robust, scalable translation services with effective inter-component communication.

Installation
To get started with this project, follow these instructions:

Clone the repository: git clone https://github.com/username/CapstoneProject.git
Navigate to the project directory: cd CapstoneProject
Install Python dependencies from the requirements.txt file: pip install -r requirements.txt
Ensure Docker is installed on your system. If not, download and install it from Docker's official website.
Pull the LibreTranslate Docker image and run it: docker pull libretranslate/libretranslate and docker run -ti -p 5000:5000 libretranslate/libretranslate
Similarly, download and run the RabbitMQ Docker image: docker pull rabbitmq and docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management
Usage
After installation:

Ensure the Docker containers for LibreTranslate and RabbitMQ are running.
Start the Python application.
Access the web interface via http://localhost:5000. This assumes your Python application serves a web interface on this port.
Contributing
We encourage contributions. To contribute:

Fork the repository.
Create your feature branch: git checkout -b feature/YourFeature
Commit your changes: git commit -m 'Add YourFeature'
Push to the branch: git push origin feature/YourFeature
Open a pull request.
