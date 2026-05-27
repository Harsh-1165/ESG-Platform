import { useState, useEffect, useCallback } from 'react';
import { normalizationAPI } from '../api/normalization';

export default function useRecords(orgId) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ limit: 50, offset: 0, count: 0 });
  const [filters, setFilters] = useState({
    source_type: '',
    scope: '',
    review_status: '',
    flagged: '',
    search: '',
  });

  const fetchRecords = useCallback(async () => {
    if (!orgId) return;
    setLoading(true);
    try {
      const params = {
        limit: pagination.limit,
        offset: pagination.offset,
      };

      if (filters.source_type) params.source_type = filters.source_type;
      if (filters.scope) params.scope = filters.scope;
      if (filters.review_status) params.review_status = filters.review_status;
      if (filters.flagged) params.flagged = filters.flagged;
      if (filters.search) params.search = filters.search;

      const response = await normalizationAPI.getRecords(params.limit, params.offset, params);
      setRecords(response.data.results || []);
      setPagination((prev) => ({ ...prev, count: response.data.count || 0 }));
    } catch (error) {
      console.error('Error fetching records:', error);
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, [orgId, pagination.limit, pagination.offset, filters]);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  const updateFilter = (name, value) => {
    setFilters((prev) => ({ ...prev, [name]: value }));
    setPagination((prev) => ({ ...prev, offset: 0 }));
  };

  const resetFilters = () => {
    setFilters({
      source_type: '',
      scope: '',
      review_status: '',
      flagged: '',
      search: '',
    });
    setPagination((prev) => ({ ...prev, offset: 0 }));
  };

  const goToPage = (offset) => {
    setPagination((prev) => ({ ...prev, offset }));
  };

  return {
    records,
    loading,
    filters,
    updateFilter,
    resetFilters,
    pagination,
    goToPage,
    refetch: fetchRecords,
  };
}
