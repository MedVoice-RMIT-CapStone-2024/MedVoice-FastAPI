# Check for gcloud and docker commands
if ! command -v gcloud &> /dev/null; then
    echo "gcloud could not be found. Please install the Google Cloud SDK."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "Docker could not be found. Please install Docker."
    exit 1
fi

# Set your variables
GCLOUD_PROJECT_ID="medvoice-2"
GCLOUD_PROJECT_LOCATION="us"  # Adjusted to just the region
REPOSITORY="gcr.io"

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project $GCLOUD_PROJECT_ID

# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker us-docker.pkg.dev

# Loop to prompt for image name and tag, then deploy
while true; do
    # List all current docker images
    echo "\nAvailable Docker images:"
    echo "====================="
    docker images
    echo "====================="
    echo "Enter the image name to deploy (or press 'q' to quit):"
    read IMAGE
    if [[ "$IMAGE" == 'q' ]]; then
        break
    fi

    echo "Enter the tag for $IMAGE (or press enter for 'latest' or press 'q' to quit):"
    read TAG
    TAG=${TAG:-latest}  # Default to 'latest' if no tag is specified

    if [[ "$TAG" == 'q' ]]; then
        break
    fi

    # Corrected REPOSITORY variable usage in tagging
    docker tag $IMAGE:$TAG us-docker.pkg.dev/$GCLOUD_PROJECT_ID/$REPOSITORY/$IMAGE:$TAG

    # Push the image to Google Artifact Registry
    docker push us-docker.pkg.dev/$GCLOUD_PROJECT_ID/$REPOSITORY/$IMAGE:$TAG

    echo "$IMAGE:$TAG has been deployed."
done

echo "Deployment process completed."