# Replicate Whisper

## Introduction
Replicate Whisper is a project that allows you to replicate data using the Replicate API. This README provides instructions on how to build the project locally and obtain the necessary API key and authorization for Google Cloud.

## Build Instructions
To build the project locally, follow the steps below:

1. Make sure you have Poetry installed on your system. If not, you can install it by following the instructions [here](https://python-poetry.org/docs/#installation).

2. Clone the repository to your local machine:
    ```shell
    git clone https://github.com/your-username/replicate-whisper.git
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

5. Run it locally
    ```shell
    poe run
    ```

6. [Optional] Between poetry and pip:
- From `poetry.lock` to `requirements.txt`
    ```shell
    poe export
    ```
- From `requirements.txt` to `poetry.lock`
    ```shell
    poe import
    ```

## Obtaining the API Key
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

## License
This project is licensed under the [MIT License](LICENSE).