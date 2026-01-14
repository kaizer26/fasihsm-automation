import React from 'react';

const RegionSelector = ({
    provinsi, kabupaten,
    selectedProv, selectedKab,
    onSelectProv, onSelectKab,
    loading
}) => {
    return (
        <div className="card card-dark">
            <div className="card-body">
                <div className="d-flex align-items-center gap-2 mb-3">
                    <i className="bi bi-geo-alt text-primary"></i>
                    <h6 className="mb-0 fw-semibold">Region Selection</h6>
                </div>

                <div className="row g-3">
                    <div className="col-12">
                        <label className="form-label text-secondary small">Provinsi</label>
                        <select
                            value={selectedProv || ''}
                            onChange={(e) => onSelectProv(e.target.value)}
                            className="form-select bg-dark text-light border-secondary"
                            disabled={loading.prov}
                        >
                            <option value="" disabled>-- Select Provinsi --</option>
                            {provinsi.map((p) => (
                                <option key={p.id} value={p.fullCode}>
                                    {p.fullCode} - {p.name}
                                </option>
                            ))}
                        </select>
                        {loading.prov && (
                            <div className="mt-1 text-secondary small">
                                <span className="spinner-border spinner-border-sm me-1"></span> Loading...
                            </div>
                        )}
                    </div>

                    <div className="col-12">
                        <label className="form-label text-secondary small">Kabupaten / Kota</label>
                        <select
                            value={selectedKab || ''}
                            onChange={(e) => onSelectKab(e.target.value)}
                            className="form-select bg-dark text-light border-secondary"
                            disabled={!selectedProv || loading.kab}
                        >
                            <option value="" disabled>-- Select Kabupaten --</option>
                            {kabupaten.map((k) => (
                                <option key={k.id} value={k.id}>
                                    {k.fullCode} - {k.name}
                                </option>
                            ))}
                        </select>
                        {loading.kab && (
                            <div className="mt-1 text-secondary small">
                                <span className="spinner-border spinner-border-sm me-1"></span> Loading...
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegionSelector;
