# FastAPI for MedVoice
This is the Backend for MedVoice project. This includes the ML pipeline for Whisper-Diarization, Llama and Picovoice models.

## Build Instructions
To build the project locally, follow the steps below:

1. Make sure you have Poetry installed on your system. If not, you can install it by following the instructions [here](https://python-poetry.org/docs/#installation).

2. Clone the repository to your local machine:
    ```shell
    git clone https://github.com/MedVoice-RMIT-CapStone-2024/replicate-whisper.git
    ```

3. Create and activate a Python virtual environment:
    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

4. Install the project dependencies using `Poetry`:
    ```shell
    poetry install
    ```
- Or with `Pip`
    ```shell
    pip install -r requirements.txt
    ```

5. Run the project locally:
    ```shell
    poe run
    ```

6. **[Optional]** More ultility options:
- From `poetry.lock` to `requirements.txt`
    ```shell
    poe export
    ```
- From `requirements.txt` to `poetry.lock`
    ```shell
    poe import
    ```
- To remove all the files from `audios/` and `outputs/`:
    ```shell
    poe flush
    ```

### Build project with Docker

#### Delete all containers

To delete all containers, you can use the following command:

```bash
docker rm $(docker ps -a -q)
```

#### Delete an image

To delete a specific image, first get the IMAGE ID by using:

```bash
docker images
```

Then you can remove the image using its ID as follows:

```bash
docker rmi <IMAGE_ID>
```

#### Delete all images

To delete all images, you can use the following command:

```bash
docker rmi $(docker images -q)
```

#### Push a local image to Docker Hub

- First, log in to Docker Hub:

```bash
docker login
```

- Then, tag your image with your Docker Hub username and the repository name:

```bash
docker tag <IMAGE_ID> <DOCKER_HUB_USERNAME>/<REPOSITORY_NAME>:<TAG>
```

- Then, push the image to Docker Hub:

```bash
docker push <DOCKER_HUB_USERNAME>/<REPOSITORY_NAME>:<TAG>
```

#### Pull an Image

To pull an image from a registry such as Docker Hub, use the following command:

```bash
docker pull <DOCKER_HUB_USERNAME>/<REPOSITORY_NAME>:<TAG>
```

#### Run an image

To run an image in a new container, use the following command:

```bash
docker run -d -p <HOST_PORT>:<CONTAINER_PORT> <DOCKER_HUB_USERNAME>/<REPOSITORY_NAME>:<TAG>
```

#### Docker Compose up

To start all services defined in a `docker-compose.yml` file, navigate to the directory containing the file and use the following command:

```bash
docker-compose up
```
```
Please replace `<IMAGE_ID>`, `<DOCKER_HUB_USERNAME>`, `<REPOSITORY_NAME>`, `<TAG>`, `<HOST_PORT>`, and `<CONTAINER_PORT>` with your actual values.
```

## Obtaining the Replicate API Key

To use the Replicate API, you need to obtain an API key. Follow the steps below to get your API key:

1. Visit the Replicate website at [https://www.replicate.ai](https://www.replicate.ai) and sign in to your account.

2. Navigate to your account settings and locate the API key section.

3. Generate a new API key and copy it to your clipboard.

4. In your project, create a file named `.env` in the root directory.

5. Add the following line to the `.env` file, replacing `<YOUR_API_KEY>` with your actual API key:
    ```
    REPLICATE_API_KEY=<YOUR_API_KEY>
    ```
    or your can run this command in your terminal: `export REPLICATE_API_KEY=<YOUR_API_KEY>`

## Authorizing Google Cloud

***When interacting with Google Cloud Client libraries, the library can auto-detect the credentials to use.
Make sure to follow these additional steps:***

#### 1. Set up Application Default Credentials (ADC) as described in the [Google Cloud documentation](https://cloud.google.com/docs/authentication/external/set-up-adc).

To provide your user credentials to ADC for a Google Account, you use the Google Cloud CLI:

- [Install and initialize the gcloud CLI.](https://cloud.google.com/sdk/docs/install#linux)

When you initialize the gcloud CLI, be sure to specify a Google Cloud project in which you have permission to access the resources your application needs.

- Create your credential file:
```shell
gcloud auth application-default login
```
- A sign-in screen appears. After you sign in, your credentials are stored in the local credential file used by ADC.
#### 2. Replace the `project` variable in the code with your actual project ID.
#### 3. Ensure that the user account or service account you are using has the required permissions. For this sample, you must have the "storage.buckets.list" permission.
```
Args:
    project_id: The project id of your Google Cloud project.
```

## Configuring ngrok

Run the following command to find your ngrok configuration file:

```shell
ngrok config check
```

For more information on the ngrok configuration, refer to [Ngrok Configuration]("https://ngrok.com/docs/agent/config/").
## License
This project is licensed under the [MIT License](LICENSE).
