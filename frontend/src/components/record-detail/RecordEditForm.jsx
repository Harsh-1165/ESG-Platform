import React, { useState } from 'react';

export default function RecordEditForm({ record, onSave, onCancel, loading = false }) {
  const [formData, setFormData] = useState({
    emission_quantity: record.emission_quantity || '',
    emission_unit: record.emission_unit || 'kg_CO2e',
    metric_type: record.metric_type || '',
    facility_id: record.facility_id || '',
    time_period: record.time_period || '',
    notes: record.notes || '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Quantity</label>
          <input
            type="number"
            name="emission_quantity"
            value={formData.emission_quantity}
            onChange={handleChange}
            step="0.01"
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Unit</label>
          <select
            name="emission_unit"
            value={formData.emission_unit}
            onChange={handleChange}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          >
            <option value="kg_CO2e">Kilograms CO2e</option>
            <option value="metric_tons_CO2e">Metric Tons CO2e</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Scope</label>
          <select
            name="metric_type"
            value={formData.metric_type}
            onChange={handleChange}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          >
            <option value="scope_1">Scope 1</option>
            <option value="scope_2">Scope 2</option>
            <option value="scope_3">Scope 3</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Facility ID</label>
          <input
            type="text"
            name="facility_id"
            value={formData.facility_id}
            onChange={handleChange}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Period</label>
        <input
          type="date"
          name="time_period"
          value={formData.time_period}
          onChange={handleChange}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Notes</label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows="3"
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        />
      </div>

      <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-200">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? 'Saving…' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
}
