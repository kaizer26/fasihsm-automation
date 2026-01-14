import React from 'react';

const PeriodSelector = ({ periods, selectedId, onSelect }) => {
    return (
        <div className="card card-dark">
            <div className="card-body">
                <div className="d-flex align-items-center gap-2 mb-3">
                    <i className="bi bi-calendar3 text-success"></i>
                    <h6 className="mb-0 fw-semibold">Select Period</h6>
                </div>

                <select
                    value={selectedId || ''}
                    onChange={(e) => onSelect(e.target.value)}
                    className="form-select bg-dark text-light border-secondary"
                >
                    <option value="" disabled>-- Choose a Period --</option>
                    {periods.map((p) => (
                        <option key={p.id} value={p.id}>
                            {p.name}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
};

export default PeriodSelector;
