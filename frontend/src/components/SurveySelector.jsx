import React from 'react';

const SurveySelector = ({ surveys, selectedId, onSelect, loading }) => {
    return (
        <div className="card card-dark">
            <div className="card-body">
                <div className="d-flex align-items-center gap-2 mb-3">
                    <i className="bi bi-clipboard-data text-info"></i>
                    <h6 className="mb-0 fw-semibold">Select Survey</h6>
                </div>

                <select
                    value={selectedId || ''}
                    onChange={(e) => onSelect(e.target.value)}
                    className="form-select bg-dark text-light border-secondary"
                    disabled={loading}
                >
                    <option value="" disabled>-- Choose a Survey --</option>
                    {surveys.map((s) => (
                        <option key={s.id} value={s.id}>
                            {s.name}
                        </option>
                    ))}
                </select>

                {loading && (
                    <div className="mt-2 text-secondary small">
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Loading surveys...
                    </div>
                )}
            </div>
        </div>
    );
};

export default SurveySelector;
