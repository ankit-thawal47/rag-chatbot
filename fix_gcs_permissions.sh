#!/bin/bash
# Fix GCS permissions for the service account

# Set your project and bucket details
PROJECT_ID="project-rag-storage"
SERVICE_ACCOUNT="rag-storage-documents@project-rag-storage.iam.gserviceaccount.com"
BUCKET_NAME="rag-document-store"

echo "Adding Storage Object Admin role to service account..."

# Method 1: Add role at project level (Storage Object Admin includes create, get, delete permissions)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectAdmin"

# Method 2: Alternative - Add role at bucket level (more specific)
# gsutil iam ch serviceAccount:$SERVICE_ACCOUNT:objectCreator gs://$BUCKET_NAME

echo "Permissions updated. The service account should now be able to create objects in GCS."
echo "You may need to wait a few minutes for permissions to propagate."