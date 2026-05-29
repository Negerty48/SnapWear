'use client';

import { BlobServiceClient } from '@azure/storage-blob';

const connectionString = process.env.NEXT_PUBLIC_AZURE_STORAGE_CONNECTION_STRING;
const containerName = process.env.NEXT_PUBLIC_BLOB_CONTAINER_NAME || 'photos';

/**
 * Get a SAS URL for a blob in Azure Storage
 * @param blobName - Name of the blob (image filename)
 * @returns Full URL to access the blob
 */
export async function getBlobUrl(blobName: string): Promise<string> {
  if (!connectionString) {
    throw new Error('NEXT_PUBLIC_AZURE_STORAGE_CONNECTION_STRING not configured');
  }

  try {
    const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);
    const containerClient = blobServiceClient.getContainerClient(containerName);
    const blockBlobClient = containerClient.getBlockBlobClient(blobName);
    
    // Return the URL directly (blobs are public)
    return blockBlobClient.url;
  } catch (error) {
    console.error('Error getting blob URL:', error);
    throw error;
  }
}

/**
 * Get direct blob URL without SDK (if blobs are public)
 * @param blobName - Name of the blob
 * @returns Full URL
 */
export function getDirectBlobUrl(blobName: string): string {
  const accountName = 'trendysa';
  return `https://${accountName}.blob.core.windows.net/${containerName}/${blobName}`;
}
