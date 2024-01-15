python -m vosk download-models

# CapstoneProject

## Description

CapstoneProject is a cutting-edge project focused on enhancing language translation capabilities. It leverages the LibreTranslate API and employs a RabbitMQ server to ensure efficient and reliable message queuing. This setup is ideal for applications requiring robust, scalable translation services with effective inter-component communication.

## Installation

To get started with this project, follow these instructions:

1. Clone the repository: `git clone https://github.com/username/CapstoneProject.git`
2. Navigate to the project directory: `cd CapstoneProject`
3. Install Python dependencies from the requirements.txt file: `pip install -r requirements.txt`
4. Ensure Docker is installed on your system. If not, download and install it from Docker's official website.
5. Pull the LibreTranslate Docker image and run it: `docker pull libretranslate/libretranslate` and `docker run -ti -p 5000:5000 libretranslate/libretranslate`
6. Similarly, download and run the RabbitMQ Docker image: `docker pull rabbitmq` and `docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management`
   To add VOSK to the project, follow these additional steps:

7. Install VOSK dependencies.
8. Integrate VOSK into your Python application.
9. Configure VOSK settings.
10. Download the required VOSK models: `python -m vosk download-models`.
11. Test and verify VOSK functionality.

## Usage

After installation:

1. Ensure the Docker containers for LibreTranslate and RabbitMQ are running.
2. Start the Python application.
3. Access the web interface via http://localhost:5000. This assumes your Python application serves a web interface on this port.

## Contributing

We encourage contributions. To contribute:

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a pull request.
