## How to Create a Service Account and Download JSON Credentials in GCP Console

This guide explains how to create a Google Cloud Platform (GCP) service account and download its JSON credentials file.

**Ensure you have a `.env` file in the root directory with the following variables:**
  ```env
  GCLOUD_PROJECT_ID=
  GCLOUD_STORAGE_BUCKET=
  ```

---

### Steps

#### 1. **Open Google Cloud Console**
Visit the [Google Cloud Console](https://console.cloud.google.com/).

#### 2. **Select a Project**
- Click on the **project dropdown** in the top navigation bar.
- Select an existing project or click **"New Project"** to create one.

#### 3. **Navigate to Service Accounts**
- In the left-hand navigation menu, go to **"IAM & Admin"** > **"Service Accounts"**.

#### 4. **Create a Service Account**
- Click **"Create Service Account"**.
- Fill in the details:
  - **Service Account Name**: A meaningful name (e.g., `my-service-account`).
  - **Service Account ID**: Automatically generated from the name.
  - **Description**: Optional description for the service account.
- Click **"Create and Continue"**.

#### 5. **Assign Permissions**
- Select a role for the service account:
  - **Viewer**: Read-only access.
  - **Editor**: Read-write access.
  - **Owner**: Full access.
  - Or choose a specific role like **Storage Admin**, **Compute Admin**, etc.
- Click **"Continue"**.

#### 6. **Skip Optional Grant Access**
- Skip the step to grant users access to the service account.
- Click **"Done"**.

#### 7. **Download JSON Key**
- Locate the newly created service account in the list.
- Click the **three dots menu** (⋮) under "Actions" next to the service account.
- Select **"Manage Keys"**.
- Click **"Add Key"** > **"Create New Key"**.
- Choose **"JSON"** as the key type.
- Click **"Create"**.
- The JSON file will be downloaded automatically.

#### 8. **Secure the JSON File**
- Store the file securely as it contains sensitive credentials.
- Avoid uploading it to public repositories.

#### 9. **Set the Environment Variable**
- At the root repository, rename `google-credentials.example.json` as `google-credentials.json`
- Replace its content with your newly created JSON credentials file
