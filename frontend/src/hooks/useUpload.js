import { useState } from 'react';
import { ingestionAPI } from '../api/normalization';

const initialStatus = { type: '', message: '' };

export default function useUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [sourceType, setSourceType] = useState('SAP_FUEL');
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(initialStatus);
  const [summary, setSummary] = useState(null);

  const reset = () => {
    setStatus(initialStatus);
    setSummary(null);
  };

  const parseSummary = (data = {}) => {
    return {
      totalRows: data.row_count ?? data.total_rows ?? null,
      succeeded: data.success_count ?? data.successful_rows ?? data.succeeded_rows ?? null,
      failed: data.failed_count ?? data.failed_rows ?? null,
      flagged: data.flagged_count ?? data.flagged_rows ?? null,
      detail: data,
    };
  };

  const upload = async (file, selectedSourceType) => {
    if (!file) {
      setStatus({ type: 'error', message: 'Please select a CSV file before uploading.' });
      return null;
    }

    setUploading(true);
    setStatus({ type: 'busy', message: 'Uploading file…' });
    setSummary(null);

    try {
      const response = await ingestionAPI.uploadFile(file, selectedSourceType);
      const data = response.data || {};
      const uploadSummary = parseSummary(data);
      setSummary(uploadSummary);
      setStatus({ type: 'success', message: 'Upload completed successfully.' });
      return uploadSummary;
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Upload failed.';
      setStatus({ type: 'error', message: errorMessage });
      return null;
    } finally {
      setUploading(false);
    }
  };

  return {
    selectedFile,
    setSelectedFile,
    sourceType,
    setSourceType,
    uploading,
    status,
    summary,
    upload,
    reset,
  };
}
