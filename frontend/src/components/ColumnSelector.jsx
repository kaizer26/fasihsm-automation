import React, { useState, useEffect } from 'react';

const ColumnSelector = ({ isOpen, columns, selectedColumns, onConfirm, onCancel }) => {
    const [selected, setSelected] = useState(new Set(selectedColumns));
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        // Columns already sorted by backend with smart ordering
        // If no previous selection, select all
        if (selectedColumns.length === 0 && columns.length > 0) {
            setSelected(new Set(columns));
        }
    }, [columns, selectedColumns]);

    const toggleColumn = (col) => {
        const newSelected = new Set(selected);
        if (newSelected.has(col)) {
            newSelected.delete(col);
        } else {
            newSelected.add(col);
        }
        setSelected(newSelected);
    };

    const selectAll = () => setSelected(new Set(columns));
    const selectNone = () => setSelected(new Set());

    const filteredColumns = columns.filter(col =>
        col.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleConfirm = () => {
        // Return columns in the order they appear in backend (smart sorted)
        const orderedSelection = columns.filter(col => selected.has(col));
        onConfirm(orderedSelection);
    };

    if (!isOpen) return null;

    return (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.7)' }}>
            <div className="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                <div className="modal-content bg-dark text-light border-secondary">
                    <div className="modal-header border-secondary">
                        <h5 className="modal-title">
                            <i className="bi bi-columns-gap me-2 text-primary"></i>
                            Pilih Kolom untuk Download
                        </h5>
                        <button type="button" className="btn-close btn-close-white" onClick={onCancel}></button>
                    </div>

                    <div className="modal-body">
                        {/* Search and Actions */}
                        <div className="row g-2 mb-3">
                            <div className="col-md-6">
                                <div className="input-group">
                                    <span className="input-group-text bg-dark border-secondary">
                                        <i className="bi bi-search text-secondary"></i>
                                    </span>
                                    <input
                                        type="text"
                                        className="form-control bg-dark text-light border-secondary"
                                        placeholder="Cari kolom..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                    />
                                </div>
                            </div>
                            <div className="col-md-6 d-flex gap-2 justify-content-md-end">
                                <button className="btn btn-sm btn-outline-success" onClick={selectAll}>
                                    <i className="bi bi-check-all me-1"></i> Select All
                                </button>
                                <button className="btn btn-sm btn-outline-warning" onClick={selectNone}>
                                    <i className="bi bi-x-lg me-1"></i> Clear All
                                </button>
                            </div>
                        </div>

                        {/* Column List */}
                        <div className="border border-secondary rounded p-2" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            <div className="row g-2">
                                {filteredColumns.map((col, idx) => (
                                    <div key={idx} className="col-md-6 col-lg-4">
                                        <div
                                            className={`p-2 rounded cursor-pointer d-flex align-items-center gap-2 ${selected.has(col)
                                                    ? 'bg-primary bg-opacity-25 border border-primary'
                                                    : 'bg-secondary bg-opacity-10 border border-secondary'
                                                }`}
                                            onClick={() => toggleColumn(col)}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            <i className={`bi ${selected.has(col) ? 'bi-check-square-fill text-primary' : 'bi-square text-secondary'}`}></i>
                                            <span className="small text-truncate" title={col}>{col}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Info */}
                        <div className="mt-3 text-secondary small">
                            <i className="bi bi-info-circle me-1"></i>
                            {selected.size} dari {columns.length} kolom dipilih. Kolom diurutkan berdasarkan blok pertanyaan.
                        </div>
                    </div>

                    <div className="modal-footer border-secondary">
                        <button type="button" className="btn btn-secondary" onClick={onCancel}>
                            Batal
                        </button>
                        <button
                            type="button"
                            className="btn btn-primary d-flex align-items-center gap-2"
                            onClick={handleConfirm}
                            disabled={selected.size === 0}
                        >
                            <i className="bi bi-download"></i>
                            Download ({selected.size} kolom)
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ColumnSelector;
