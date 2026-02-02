import React, { useEffect, useState, useRef } from 'react';
import { actionService } from '../services/api';

const ProgressViewer = ({ taskId, onClose }) => {
    const [progress, setProgress] = useState({ status: 'initializing', progress: 0, logs: [], message: 'Starting...' });
    const [downloadUrl, setDownloadUrl] = useState(null);
    const logsEndRef = useRef(null);

    useEffect(() => {
        let interval;
        if (taskId) {
            interval = setInterval(async () => {
                try {
                    const res = await actionService.getProgress(taskId);
                    if (res.data.success) {
                        const data = res.data.data;
                        setProgress(data);

                        if (data.status === 'completed' || data.status === 'error') {
                            clearInterval(interval);
                            if (data.filename) {
                                setDownloadUrl(actionService.getDownloadUrl(data.filename));
                            }
                        }
                    }
                } catch (err) {
                    console.error(err);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [taskId]);

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [progress.logs]);

    const getProgressVariant = () => {
        if (progress.status === 'completed') return 'bg-success';
        if (progress.status === 'error') return 'bg-danger';
        return 'bg-primary';
    };

    const getStatusBadge = () => {
        if (progress.status === 'completed') return <span className="badge bg-success">Completed</span>;
        if (progress.status === 'error') return <span className="badge bg-danger">Error</span>;
        if (progress.status === 'running') return <span className="badge bg-primary animate-pulse-slow">Running</span>;
        return <span className="badge bg-secondary">Initializing</span>;
    };

    return (
        <div className="card card-dark mt-4">
            <div className="card-body">
                <div className="d-flex justify-content-between align-items-center mb-3">
                    <div className="d-flex align-items-center gap-2">
                        <i className="bi bi-terminal text-secondary"></i>
                        <span className="text-uppercase text-secondary small fw-semibold">Task Execution Log</span>
                    </div>
                    {getStatusBadge()}
                </div>

                {/* Summary Metrics */}
                {(progress.total_assignments > 0) && (
                    <div className="row g-2 mb-3">
                        <div className="col-3">
                            <div className="bg-dark border border-secondary rounded p-2 text-center">
                                <small className="text-secondary d-block">Total</small>
                                <span className="fw-bold text-light">{progress.total_assignments}</span>
                            </div>
                        </div>
                        <div className="col-3">
                            <div className="bg-dark border border-success rounded p-2 text-center">
                                <small className="text-success d-block">Success</small>
                                <span className="fw-bold text-success">{progress.success_count || 0}</span>
                            </div>
                        </div>
                        <div className="col-3">
                            <div className="bg-dark border border-danger rounded p-2 text-center">
                                <small className="text-danger d-block">Failed</small>
                                <span className="fw-bold text-danger">{progress.fail_count || 0}</span>
                            </div>
                        </div>
                        <div className="col-3">
                            <div className="bg-dark border border-info rounded p-2 text-center">
                                <small className="text-info d-block">Skipped</small>
                                <span className="fw-bold text-info">{progress.skip_count || 0}</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Progress Info */}
                <div className="mb-3">
                    <div className="d-flex justify-content-between align-items-center mb-1">
                        <span className="small text-light">{progress.message}</span>
                        <span className="small text-secondary">{progress.progress}%</span>
                    </div>
                    <div className="progress" style={{ height: '8px' }}>
                        <div
                            className={`progress-bar ${getProgressVariant()}`}
                            role="progressbar"
                            style={{ width: `${progress.progress}%`, transition: 'width 0.3s ease' }}
                        ></div>
                    </div>
                </div>

                {/* Log Terminal */}
                <div className="log-terminal rounded p-3 border border-secondary overflow-auto" style={{ maxHeight: '250px' }}>
                    {progress.logs && progress.logs.map((log, i) => (
                        <div key={i} className="text-light mb-1 pb-1 border-bottom border-secondary" style={{ fontSize: '0.8rem' }}>
                            <span className="text-secondary me-2">[{new Date().toLocaleTimeString()}]</span>
                            {log}
                        </div>
                    ))}
                    <div ref={logsEndRef} />
                </div>

                {/* Action Buttons */}
                <div className="mt-3 d-flex justify-content-end gap-2">
                    {downloadUrl && (
                        <a
                            href={downloadUrl}
                            download
                            className="btn btn-success btn-sm d-flex align-items-center gap-2"
                        >
                            <i className="bi bi-download"></i> Download Result
                        </a>
                    )}
                    {(progress.status === 'completed' || progress.status === 'error') && (
                        <button onClick={onClose} className="btn btn-secondary btn-sm">
                            Close
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProgressViewer;
