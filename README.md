# FastAPI for MedVoice
This is the Backend for MedVoice project. This includes the ML pipeline for Whisper-Diarization, Llama and Picovoice models.

## Build Instructions
To build the project locally, follow the steps below:

***Note:*** This `README` will assume that your machine is UNIX-based. Please find the equivalent command if you are running on a Windows machine.

1. Clone the repository to your local machine:
    ```shell
    git clone https://github.com/MedVoice-RMIT-CapStone-2024/MedVoice-FastAPI.git
    ```

2. Install `make` command:
- On Ubuntu or other Debian-based systems, you can use `apt-get`:
    ```shell
    sudo apt-get install make
    ```

3. Install the project dependencies using `make`:
    ```shell
    make setup
    ```
- In your local environment, remove the `-placeholder.txt` from `.env` and `ngrok.yml` for the neccessary dependencies.

4. Check for missing dependencies and files:
    ```shell
    make check
    ```
*You should install the missing dependencies and files accordingly*

5. Run the project locally:
    ```shell
    poe compose # or poe compose2
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

#### Docker Compose up

To start all services defined in a `docker-compose.yml` file, navigate to the directory containing the file and use the following command:

```bash
docker-compose build --no-cache
docker-compose up --build
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
