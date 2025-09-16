#!/bin/bash

# ANSI color codes for prettier output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function for displaying section headers
print_header() {
    echo -e "\n${BOLD}${BLUE}======================================${NC}"
    echo -e "${BOLD}${BLUE}   $1${NC}"
    echo -e "${BOLD}${BLUE}======================================${NC}\n"
}

# Function for success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function for error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function for info messages
print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Function for warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_header "S3 DATA LOADING UTILITY"
print_info "Starting data transfer process at $(date '+%Y-%m-%d %H:%M:%S')"

# Find the S3 bucket name that starts with csv-file-store
print_info "Searching for S3 bucket with prefix 'csv-file-store'..."
S3_BUCKET=$(aws s3 ls | grep csv-file-store | awk '{print $3}')

if [ -z "$S3_BUCKET" ]; then
    print_error "Could not find S3 bucket starting with csv-file-store"
    exit 1
fi

print_success "Found target S3 bucket: ${BOLD}$S3_BUCKET${NC}"

# Create a datasets directory if it doesn't exist
print_info "Setting up local environment..."
mkdir -p datasets
print_success "Created datasets directory for temporary storage"

# List of files to download and upload
FILES=(
    "payment_history.csv"
    "customer_service_interactions.csv"
    "product_usage.csv"
    "customer_table.csv"
    "transaction_history.csv"
    "product_table.csv"
    "liability_table.csv"
)

# Source bucket path
SOURCE_BUCKET="s3://ws-assets-prod-iad-r-pdx-f3b3f9f1a7d6a3d0/d907665b-30b5-4b48-9368-8c67642d67de/data"
print_info "Source bucket: ${BOLD}$SOURCE_BUCKET${NC}"
print_info "Target bucket: ${BOLD}s3://$S3_BUCKET/datalake-csv/...${NC}"

# Display total files to process
TOTAL_FILES=${#FILES[@]}
print_info "Preparing to process ${BOLD}$TOTAL_FILES${NC} files"

# Process each file
COUNTER=0
SUCCESSFUL=0
FAILED=0

for FILE in "${FILES[@]}"; do
    COUNTER=$((COUNTER+1))
    print_header "PROCESSING FILE $COUNTER/$TOTAL_FILES: $FILE"

    # Step 1: Download the file to CloudShell
    print_info "Downloading $FILE from source bucket..."
    aws s3 cp "$SOURCE_BUCKET/$FILE" "datasets/$FILE"

    if [ $? -ne 0 ]; then
        print_error "Failed to download $FILE"
        FAILED=$((FAILED+1))
        continue
    fi

    print_success "Downloaded $FILE successfully"

    # Determine the destination path based on the file name
    case "$FILE" in
        payment_history.csv)
            DEST_PATH="datalake-csv/payment_history"
            ;;
        customer_service_interactions.csv)
            DEST_PATH="datalake-csv/cust_service_interaction"
            ;;
        product_usage.csv)
            DEST_PATH="datalake-csv/product_usage"
            ;;
        customer_table.csv)
            DEST_PATH="datalake-csv/customer"
            ;;
        transaction_history.csv)
            DEST_PATH="datalake-csv/transaction_history"
            ;;
        product_table.csv)
            DEST_PATH="datalake-csv/product"
            ;;
        liability_table.csv)
            DEST_PATH="datalake-csv/liabilities"
            ;;
        *)
            DEST_PATH="datalake-csv/$(basename "$FILE" .csv)"
            ;;
    esac

    # Step 2: Upload the file to the destination bucket
    print_info "Uploading $FILE to s3://$S3_BUCKET/$DEST_PATH/"
    aws s3 cp "datasets/$FILE" "s3://$S3_BUCKET/$DEST_PATH/"

    if [ $? -ne 0 ]; then
        print_error "Failed to upload $FILE to destination"
        FAILED=$((FAILED+1))
    else
        print_success "Successfully transferred $FILE to s3://$S3_BUCKET/$DEST_PATH/"
        SUCCESSFUL=$((SUCCESSFUL+1))
    fi

    # Show a small separator between files
    echo -e "${YELLOW}----------------------------------------${NC}"
done

print_header "DATA LOADING SUMMARY"
print_info "Total files processed: ${BOLD}$TOTAL_FILES${NC}"
print_success "Successfully transferred: ${BOLD}$SUCCESSFUL${NC}"
if [ $FAILED -gt 0 ]; then
    print_error "Failed transfers: ${BOLD}$FAILED${NC}"
fi

if [ $SUCCESSFUL -eq $TOTAL_FILES ]; then
    print_header "DATA LOADING COMPLETE"
    print_success "All files were successfully transferred to your S3 bucket!"
    print_info "The AUTO COPY jobs should now begin loading data into your Redshift tables."
    print_info "Completed at $(date '+%Y-%m-%d %H:%M:%S')"
else
    print_header "DATA LOADING INCOMPLETE"
    print_warning "Some files failed to transfer. Please check the logs above for details."
    print_info "Completed with errors at $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Clean up temporary files
print_info "Cleaning up temporary files..."
rm -rf datasets
print_success "Cleanup complete"