import React, { useState, useEffect } from 'react';
import { actionService } from '../services/api';
import ColumnSelector from './ColumnSelector';

const HistoryPanel = ({ refreshTrigger }) => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Column selector state
    const [showColumnSelector, setShowColumnSelector] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [availableColumns, setAvailableColumns] = useState([]);
    const [loadingColumns, setLoadingColumns] = useState(false);
    const [exporting, setExporting] = useState(false);

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

    // Handle download button click - show column selector for raw_data files
    const handleDownloadClick = async (item) => {
        if (item.type !== 'raw_data') {
            // Log files: direct download
            window.location.href = actionService.getDownloadUrl(item.filename);
            return;
        }

        // Raw data files: show column selector
        setSelectedFile(item);
        setLoadingColumns(true);

        try {
            const res = await actionService.getFileColumns(item.filename);
            if (res.data.success) {
                setAvailableColumns(res.data.columns);
                setShowColumnSelector(true);
            } else {
                // Fallback: direct download if can't get columns
                window.location.href = actionService.getDownloadUrl(item.filename);
            }
        } catch (err) {
            console.error('Failed to load columns:', err);
            // Fallback: direct download
            window.location.href = actionService.getDownloadUrl(item.filename);
        } finally {
            setLoadingColumns(false);
        }
    };

    // Handle column selection confirmation
    const handleColumnConfirm = async (columns) => {
        if (!selectedFile) return;

        setExporting(true);
        setShowColumnSelector(false);

        try {
            const res = await actionService.exportFiltered(selectedFile.filename, columns);
            if (res.data.success) {
                // Download the filtered file
                window.location.href = actionService.getDownloadUrl(res.data.filename);
                // Refresh history to show the new filtered file
                loadHistory();
            } else {
                alert('Failed to export: ' + res.data.message);
            }
        } catch (err) {
            console.error('Export failed:', err);
            alert('Failed to export filtered data');
        } finally {
            setExporting(false);
            setSelectedFile(null);
        }
    };

    const handleCancelColumnSelector = () => {
        setShowColumnSelector(false);
        setSelectedFile(null);
    };

    return (
        <>
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
                                                <button
                                                    onClick={() => handleDownloadClick(item)}
                                                    className="btn btn-sm btn-icon btn-outline-info"
                                                    disabled={loadingColumns && selectedFile?.filename === item.filename}
                                                    title={item.type === 'raw_data' ? 'Select columns and download' : 'Download'}
                                                >
                                                    {loadingColumns && selectedFile?.filename === item.filename ? (
                                                        <span className="spinner-border spinner-border-sm"></span>
                                                    ) : (
                                                        <i className="bi bi-download"></i>
                                                    )}
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Tip message */}
                    <div className="mt-2 text-secondary small">
                        <i className="bi bi-lightbulb me-1"></i>
                        Klik download pada Raw Data untuk memilih kolom sebelum download
                    </div>
                </div>
            </div>

            {/* Column Selector Modal */}
            <ColumnSelector
                isOpen={showColumnSelector}
                columns={availableColumns}
                selectedColumns={[]}
                onConfirm={handleColumnConfirm}
                onCancel={handleCancelColumnSelector}
            />

            {/* Exporting Overlay */}
            {exporting && (
                <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.7)' }}>
                    <div className="modal-dialog modal-dialog-centered">
                        <div className="modal-content bg-dark text-light border-secondary text-center p-4">
                            <div className="spinner-border text-primary mb-3" role="status"></div>
                            <p className="mb-0">Exporting filtered data...</p>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default HistoryPanel;
