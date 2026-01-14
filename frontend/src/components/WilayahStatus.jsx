import React from 'react';

const WilayahStatus = ({ status, loading, onRefresh }) => {
    const getStatusDisplay = () => {
        switch (status.status) {
            case 'checking':
                return {
                    icon: 'bi-hourglass-split',
                    text: 'Checking cache...',
                    variant: 'badge-loading',
                    color: 'text-info'
                };
            case 'fetching':
                return {
                    icon: 'bi-cloud-download',
                    text: 'Fetching from FASIH-SM...',
                    variant: 'badge-loading',
                    color: 'text-info'
                };
            case 'ready':
                return {
                    icon: 'bi-check-circle-fill',
                    text: `Ready (${status.count} smallcodes)`,
                    variant: 'badge-ready',
                    color: 'text-success'
                };
            case 'error':
                return {
                    icon: 'bi-exclamation-triangle-fill',
                    text: 'Failed to load wilayah',
                    variant: 'badge-error',
                    color: 'text-danger'
                };
            default:
                return {
                    icon: 'bi-dash-circle',
                    text: 'Not loaded',
                    variant: 'bg-secondary',
                    color: 'text-secondary'
                };
        }
    };

    const display = getStatusDisplay();

    return (
        <div className="card card-dark">
            <div className="card-body">
                <div className="d-flex align-items-center justify-content-between">
                    <div className="d-flex align-items-center gap-2">
                        <i className="bi bi-map text-warning"></i>
                        <h6 className="mb-0 fw-semibold">Daftar Wilayah</h6>
                    </div>

                    {status.status === 'error' && (
                        <button
                            onClick={onRefresh}
                            className="btn btn-outline-warning btn-sm"
                            disabled={loading}
                        >
                            <i className="bi bi-arrow-clockwise"></i>
                        </button>
                    )}
                </div>

                <div className="mt-3">
                    <div className={`d-flex align-items-center gap-2 ${display.color}`}>
                        {loading ? (
                            <span className="spinner-border spinner-border-sm"></span>
                        ) : (
                            <i className={`bi ${display.icon}`}></i>
                        )}
                        <span className="small">{display.text}</span>
                    </div>

                    {status.status === 'ready' && (
                        <div className="mt-2">
                            <span className={`badge ${display.variant}`}>
                                <i className="bi bi-check me-1"></i>
                                Cache available
                            </span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WilayahStatus;
