import React from 'react';

const ActionPanel = ({ onAction, disabled, role }) => {
    // Directly trigger download without column selection
    // Column selection is now only available in Download History
    const handleDownloadClick = () => {
        onAction('download-raw', []);
    };

    return (
        <div className="card card-dark mb-4">
            <div className="card-body">
                <div className="d-flex justify-content-between align-items-center mb-3">
                    <div className="d-flex align-items-center gap-2">
                        <i className="bi bi-lightning text-warning"></i>
                        <h6 className="mb-0 fw-semibold">Actions</h6>
                    </div>
                    {role && (
                        <span className="badge bg-secondary">Role: {role}</span>
                    )}
                </div>

                <div className="row g-2">
                    <div className="col-6 col-lg-3">
                        <button
                            onClick={handleDownloadClick}
                            disabled={disabled}
                            className="btn btn-primary btn-action w-100 d-flex align-items-center justify-content-center gap-2"
                        >
                            <i className="bi bi-download"></i>
                            <span className="d-none d-sm-inline">Download</span>
                        </button>
                    </div>

                    <div className="col-6 col-lg-3">
                        <button
                            onClick={() => onAction('approve')}
                            disabled={disabled}
                            className="btn btn-success btn-action w-100 d-flex align-items-center justify-content-center gap-2"
                        >
                            <i className="bi bi-check-circle"></i>
                            <span className="d-none d-sm-inline">Approve</span>
                        </button>
                    </div>

                    <div className="col-6 col-lg-3">
                        <button
                            onClick={() => onAction('revoke')}
                            disabled={disabled}
                            className="btn btn-warning btn-action w-100 d-flex align-items-center justify-content-center gap-2"
                        >
                            <i className="bi bi-arrow-counterclockwise"></i>
                            <span className="d-none d-sm-inline">Revoke</span>
                        </button>
                    </div>

                    <div className="col-6 col-lg-3">
                        <button
                            onClick={() => onAction('reject')}
                            disabled={disabled}
                            className="btn btn-danger btn-action w-100 d-flex align-items-center justify-content-center gap-2"
                        >
                            <i className="bi bi-x-circle"></i>
                            <span className="d-none d-sm-inline">Reject</span>
                        </button>
                    </div>
                </div>

                {disabled && (
                    <div className="mt-3 text-secondary small text-center">
                        <i className="bi bi-info-circle me-1"></i>
                        Select survey, period, and kabupaten to enable actions
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActionPanel;
