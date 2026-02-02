import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, surveyService, regionService, actionService, wilayahService } from '../services/api';
import SurveySelector from '../components/SurveySelector';
import PeriodSelector from '../components/PeriodSelector';
import RegionSelector from '../components/RegionSelector';
import ActionPanel from '../components/ActionPanel';
import ProgressViewer from '../components/ProgressViewer';
import WilayahStatus from '../components/WilayahStatus';
import HistoryPanel from '../components/HistoryPanel';

const DashboardPage = () => {
    const navigate = useNavigate();

    // Data State
    const [surveys, setSurveys] = useState([]);
    const [periods, setPeriods] = useState([]);
    const [provinsi, setProvinsi] = useState([]);
    const [kabupaten, setKabupaten] = useState([]);

    // Selection State
    const [surveyId, setSurveyId] = useState('');
    const [surveyName, setSurveyName] = useState('');
    const [periodId, setPeriodId] = useState('');
    const [periodName, setPeriodName] = useState('');
    const [groupId, setGroupId] = useState('');
    const [templateId, setTemplateId] = useState('');

    const [provFullCode, setProvFullCode] = useState('');
    const [kabId, setKabId] = useState('');
    const [kabName, setKabName] = useState('');

    // User Role State
    const [role, setRole] = useState('');

    // Wilayah Status State
    const [wilayahStatus, setWilayahStatus] = useState({ status: 'idle', count: 0 });

    // UI State
    const [loading, setLoading] = useState({ surveys: false, prov: false, kab: false, wilayah: false });
    const [taskId, setTaskId] = useState(null);
    const [error, setError] = useState('');
    const [historyRefresh, setHistoryRefresh] = useState(0);

    // --- Init ---
    useEffect(() => {
        checkAuth();
        loadSurveys();
    }, []);

    const checkAuth = async () => {
        try {
            const res = await authService.checkStatus();
            if (!res.data.is_logged_in) navigate('/login');
        } catch {
            navigate('/login');
        }
    };

    const handleLogout = async () => {
        await authService.logout();
        navigate('/login');
    };

    // --- Data Loaders ---
    const loadSurveys = async () => {
        setLoading(p => ({ ...p, surveys: true }));
        try {
            const res = await surveyService.getAll();
            setSurveys(res.data.data);
        } catch (err) {
            setError('Failed to load surveys');
        } finally {
            setLoading(p => ({ ...p, surveys: false }));
        }
    };

    // --- Handlers ---
    const handleSelectSurvey = async (id) => {
        setSurveyId(id);
        const selected = surveys.find(s => s.id === id);
        setSurveyName(selected?.name || '');
        setGroupId(selected?.regionGroupId || '');

        // Reset lower levels
        setPeriodId('');
        setPeriods([]);
        setProvFullCode('');
        setKabId('');
        setProvinsi([]);
        setKabupaten([]);
        setRole('');
        setTemplateId('');
        setWilayahStatus({ status: 'idle', count: 0 });

        // Fetch detail
        try {
            const res = await surveyService.getDetail(id);
            const detail = res.data.data;
            setPeriods(detail.periods);
            setGroupId(detail.regionGroupId);
            setTemplateId(detail.templateId);
            loadProvinsi(detail.regionGroupId);
        } catch (err) {
            setError('Failed to load survey details');
        }
    };

    const loadProvinsi = async (gid) => {
        setLoading(p => ({ ...p, prov: true }));
        try {
            const res = await regionService.getProvinsi(gid);
            setProvinsi(res.data.data);
        } catch (err) {
            setError('Failed to load regions');
        } finally {
            setLoading(p => ({ ...p, prov: false }));
        }
    };

    const handleSelectPeriod = async (pid) => {
        setPeriodId(pid);
        const p = periods.find(x => x.id === pid);
        setPeriodName(p?.name || '');
        setWilayahStatus({ status: 'idle', count: 0 });

        try {
            const res = await surveyService.getUserRole(surveyId, pid);
            setRole(res.data.data.role);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSelectProv = async (code) => {
        setProvFullCode(code);
        setKabId('');
        setKabupaten([]);
        setWilayahStatus({ status: 'idle', count: 0 });

        setLoading(p => ({ ...p, kab: true }));
        try {
            const res = await regionService.getKabupaten(groupId, code);
            setKabupaten(res.data.data);
        } catch (err) {
            setError('Failed to load kabupaten');
        } finally {
            setLoading(p => ({ ...p, kab: false }));
        }
    };

    const handleSelectKab = async (id) => {
        setKabId(id);
        const k = kabupaten.find(x => x.id === id);
        setKabName(k?.name || '');

        // Auto-fetch wilayah after kabupaten selection
        if (surveyId && periodId && id && groupId) {
            await checkAndFetchWilayah(id);
        }
    };

    const checkAndFetchWilayah = async (kabId) => {
        setLoading(p => ({ ...p, wilayah: true }));
        setWilayahStatus({ status: 'checking', count: 0 });

        try {
            // Check if wilayah cache exists
            const statusRes = await wilayahService.checkStatus(surveyId, periodId, kabId);

            if (statusRes.data.exists) {
                setWilayahStatus({ status: 'ready', count: statusRes.data.count });
            } else {
                // Fetch wilayah from FASIH-SM API
                setWilayahStatus({ status: 'fetching', count: 0 });
                const fetchRes = await wilayahService.fetch({
                    surveyId, periodId, kabId, groupId
                });

                if (fetchRes.data.success) {
                    setWilayahStatus({ status: 'ready', count: fetchRes.data.count });
                } else {
                    setWilayahStatus({ status: 'error', count: 0 });
                }
            }
        } catch (err) {
            setWilayahStatus({ status: 'error', count: 0 });
            console.error('Wilayah check/fetch error:', err);
        } finally {
            setLoading(p => ({ ...p, wilayah: false }));
        }
    };

    // --- Actions ---
    const handleAction = async (type, selectedColumns = []) => {
        if (!surveyId || !periodId || !kabId) return;

        const payload = {
            surveyId, periodId, templateId, groupId, kabId,
            kabName, surveyName, periodName
        };

        // Add selected columns for download
        if (type === 'download-raw' && selectedColumns.length > 0) {
            payload.selectedColumns = selectedColumns;
        }

        try {
            let res;
            if (type === 'download-raw') res = await actionService.downloadRaw(payload);
            else if (type === 'approve') res = await actionService.approve(payload);
            else if (type === 'revoke') res = await actionService.revoke(payload);
            else if (type === 'reject') res = await actionService.reject(payload);

            if (res.data.success) {
                setTaskId(res.data.taskId);
            }
        } catch (err) {
            setError(`Action ${type} failed to start`);
        }
    };

    const canPerformAction = surveyId && periodId && kabId && wilayahStatus.status === 'ready' && !taskId;

    return (
        <div className="min-vh-100 d-flex flex-column">
            {/* Header */}
            <header className="bg-dark border-bottom border-secondary py-3 sticky-top">
                <div className="container">
                    <div className="d-flex justify-content-between align-items-center">
                        <div className="d-flex align-items-center gap-3">
                            <div className="bg-primary rounded p-2">
                                <i className="bi bi-grid-1x2 fs-4 text-white"></i>
                            </div>
                            <div>
                                <h1 className="h4 mb-0 text-gradient fw-bold">FASIH-SM</h1>
                                <small className="text-secondary">Web Automation Dashboard</small>
                            </div>
                        </div>

                        <button onClick={handleLogout} className="btn btn-outline-secondary btn-sm d-flex align-items-center gap-2">
                            <i className="bi bi-box-arrow-right"></i> Sign Out
                        </button>
                    </div>
                </div>
            </header>

            {/* Content */}
            <main className="container py-4 flex-grow-1">
                {error && (
                    <div className="alert alert-danger alert-dismissible fade show d-flex justify-content-between align-items-center" role="alert">
                        <span><i className="bi bi-exclamation-triangle me-2"></i>{error}</span>
                        <button type="button" className="btn-close" onClick={() => setError('')}></button>
                    </div>
                )}

                <div className="row g-4">
                    {/* Left Column: Selectors */}
                    <div className="col-lg-4">
                        <div className="d-flex flex-column gap-4">
                            <SurveySelector
                                surveys={surveys}
                                selectedId={surveyId}
                                onSelect={handleSelectSurvey}
                                loading={loading.surveys}
                            />

                            {surveyId && periods.length > 0 && (
                                <PeriodSelector
                                    periods={periods}
                                    selectedId={periodId}
                                    onSelect={handleSelectPeriod}
                                />
                            )}

                            {groupId && (
                                <RegionSelector
                                    provinsi={provinsi}
                                    kabupaten={kabupaten}
                                    selectedProv={provFullCode}
                                    selectedKab={kabId}
                                    onSelectProv={handleSelectProv}
                                    onSelectKab={handleSelectKab}
                                    loading={loading}
                                />
                            )}

                            {kabId && (
                                <WilayahStatus
                                    status={wilayahStatus}
                                    loading={loading.wilayah}
                                    onRefresh={() => checkAndFetchWilayah(kabId)}
                                />
                            )}
                        </div>
                    </div>

                    {/* Right Column: Context + Actions + Results */}
                    <div className="col-lg-8">
                        {/* Current Context Card */}
                        <div className="card card-dark mb-4">
                            <div className="card-body">
                                <h6 className="text-uppercase text-secondary fw-semibold mb-3">
                                    <i className="bi bi-info-circle me-2"></i>Current Context
                                </h6>
                                <div className="context-grid">
                                    <div className="bg-dark rounded p-3 border border-secondary">
                                        <small className="text-secondary d-block mb-1">Survey</small>
                                        <span className="text-info fw-medium">{surveyName || '-'}</span>
                                    </div>
                                    <div className="bg-dark rounded p-3 border border-secondary">
                                        <small className="text-secondary d-block mb-1">Period</small>
                                        <span className="text-success fw-medium">{periodName || '-'}</span>
                                    </div>
                                    <div className="bg-dark rounded p-3 border border-secondary">
                                        <small className="text-secondary d-block mb-1">Region</small>
                                        <span className="text-primary fw-medium">{kabName || '-'}</span>
                                    </div>
                                    <div className="bg-dark rounded p-3 border border-secondary">
                                        <small className="text-secondary d-block mb-1">Role</small>
                                        <span className="text-warning fw-medium">{role || '-'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <ActionPanel
                            onAction={handleAction}
                            disabled={!canPerformAction}
                            role={role}
                        />

                        {taskId && (
                            <ProgressViewer
                                taskId={taskId}
                                onClose={() => {
                                    setTaskId(null);
                                    setHistoryRefresh(prev => prev + 1);
                                }}
                            />
                        )}

                        {!taskId && (
                            <div className="d-flex flex-column gap-4">
                                <HistoryPanel refreshTrigger={historyRefresh} />

                                <div className="border border-secondary border-2 border-dashed rounded p-5 text-center text-secondary">
                                    <i className="bi bi-file-earmark-text fs-1 mb-3 d-block opacity-25"></i>
                                    <p className="mb-0">Select filters and start an action to see logs.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DashboardPage;
