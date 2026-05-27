import client from './client';

export const ingestionAPI = {
  uploadFile: (file, sourceType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', sourceType);
    return client.post('/ingestion/batches/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  getBatches: (limit = 50, offset = 0) => {
    return client.get('/ingestion/batches/', { params: { limit, offset } });
  },
  
  getBatchDetail: (batchId) => {
    return client.get(`/ingestion/batches/${batchId}/`);
  },
  
  getBatchRows: (batchId, limit = 50, offset = 0) => {
    return client.get(`/ingestion/batches/${batchId}/rows/`, { params: { limit, offset } });
  },
  
  getRowDetail: (batchId, rowId) => {
    return client.get(`/ingestion/batches/${batchId}/row_detail/`, { params: { row_id: rowId } });
  },
  
  flagRow: (batchId, rowId, isFlagged, flagReason) => {
    return client.patch(`/ingestion/batches/${batchId}/flag_row/`, {
      row_id: rowId,
      is_flagged: isFlagged,
      flag_reason: flagReason,
    });
  },
};

export const normalizationAPI = {
  getRecords: (limit = 50, offset = 0, filters = {}) => {
    return client.get('/normalization/records/', { params: { limit, offset, ...filters } });
  },
  
  getRecordDetail: (recordId) => {
    return client.get(`/normalization/records/${recordId}/`);
  },
  
  normalizeBatch: (batchId) => {
    return client.post('/normalization/records/normalize_batch/', { batch_id: batchId });
  },
  
  updateRecord: (recordId, data) => {
    return client.patch(`/normalization/records/${recordId}/update_record/`, data);
  },
  
  getHistory: (recordId, limit = 50, offset = 0) => {
    return client.get(`/normalization/records/${recordId}/history/`, { params: { limit, offset } });
  },
};

export const approvalAPI = {
  getPending: (limit = 50, offset = 0) => {
    return client.get('/approval/records/pending/', { params: { limit, offset } });
  },
  
  getRecords: (limit = 50, offset = 0, status = null) => {
    const params = { limit, offset };
    if (status) params.status = status;
    return client.get('/approval/records/', { params });
  },
  
  approve: (recordId, comment = '') => {
    return client.post(`/approval/records/${recordId}/approve/`, { comment });
  },
  
  reject: (recordId, reason = '') => {
    return client.post(`/approval/records/${recordId}/reject/`, { reason });
  },
  
  lock: (recordId, reason = '') => {
    return client.post(`/approval/records/${recordId}/lock/`, { reason });
  },
};

export const auditAPI = {
  getLogs: (limit = 50, offset = 0, filters = {}) => {
    return client.get('/audit/logs/', { params: { limit, offset, ...filters } });
  },
};
