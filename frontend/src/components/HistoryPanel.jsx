import React, { useState, useEffect } from 'react';
import { actionService } from '../services/api';

const HistoryPanel = ({ refreshTrigger }) => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const loadHistory = async () => {
        setLoading(true);
        try {
            const res = await actionService.getHistory();
            if (res.data.success) {
                setHistory(res.data.history);
            }
        } catch (err) {
            setError('Failed to load history');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadHistory();
    }, [refreshTrigger]);

    const formatSize = (bytes) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (isoStr) => {
        const date = new Date(isoStr);
        return date.toLocaleString('id-ID', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="card card-dark mb-4">
            <div className="card-body">
                <div className="d-flex justify-content-between align-items-center mb-3">
                    <div className="d-flex align-items-center gap-2">
                        <i className="bi bi-clock-history text-info"></i>
                        <h6 className="mb-0 fw-semibold">Download History</h6>
                    </div>
                    <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={loadHistory}
                        disabled={loading}
                    >
                        {loading ? <i className="spinner-border spinner-border-sm"></i> : <i className="bi bi-arrow-clockwise"></i>}
                    </button>
                </div>

                <div className="table-responsive" style={{ maxHeight: '300px' }}>
                    <table className="table table-dark table-hover table-sm small align-middle mb-0">
                        <thead className="sticky-top bg-dark">
                            <tr>
                                <th>File Name</th>
                                <th>Type</th>
                                <th>Date</th>
                                <th>Size</th>
                                <th className="text-end">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="text-center py-4 text-secondary">
                                        No history found
                                    </td>
                                </tr>
                            ) : (
                                history.map((item, idx) => (
                                    <tr key={idx}>
                                        <td>
                                            <div className="text-truncate" style={{ maxWidth: '200px' }} title={item.filename}>
                                                {item.filename}
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`badge ${item.type === 'raw_data' ? 'bg-primary' : 'bg-success'} bg-opacity-10 text-${item.type === 'raw_data' ? 'primary' : 'success'}`}>
                                                {item.type === 'raw_data' ? 'Raw Data' : 'Log'}
                                            </span>
                                        </td>
                                        <td className="text-secondary">{formatDate(item.timestamp)}</td>
                                        <td className="text-secondary">{formatSize(item.size)}</td>
                                        <td className="text-end">
                                            <a
                                                href={actionService.getDownloadUrl(item.filename)}
                                                className="btn btn-sm btn-icon btn-outline-info"
                                                download
                                            >
                                                <i className="bi bi-download"></i>
                                            </a>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default HistoryPanel;
