import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const LoginPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({ username: '', password: '', otp: '' });
    const [step, setStep] = useState('login'); // login, otp
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [statusMessage, setStatusMessage] = useState('');
    const [hasSession, setHasSession] = useState(false);
    const [otpBlocked, setOtpBlocked] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    // Check saved credentials when username changes (just get password, no validation)
    useEffect(() => {
        const checkCredentials = async () => {
            if (formData.username.length > 5) {
                try {
                    const res = await authService.checkCredentials(formData.username);
                    const { has_session, password } = res.data;

                    setHasSession(has_session);

                    if (has_session && password) {
                        setFormData(prev => ({ ...prev, password }));
                    }
                } catch (err) {
                    console.error('Credentials check error:', err);
                }
            }
        };

        const debounce = setTimeout(checkCredentials, 500);
        return () => clearTimeout(debounce);
    }, [formData.username]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (hasSession) {
            setStatusMessage('Mencoba restore session...');
        } else {
            setStatusMessage('Connecting to SSO BPS...');
        }

        try {
            const response = await authService.login(formData.username, formData.password);
            const { success, needs_otp, message, restored } = response.data;

            if (success) {
                if (restored) {
                    setStatusMessage('Session restored! Redirecting...');
                } else {
                    setStatusMessage('Login successful! Redirecting...');
                }
                setTimeout(() => navigate('/dashboard'), 1000);
            } else if (needs_otp) {
                setStep('otp');
                setStatusMessage('');
                setLoading(false);
            } else {
                setError(message || 'Login failed');
                setStatusMessage('');
                setLoading(false);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Connection error');
            setStatusMessage('');
            setLoading(false);
        }
    };

    const handleSubmitOtp = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setOtpBlocked(false);
        setStatusMessage('Verifying OTP...');

        try {
            const response = await authService.submitOtp(formData.otp);
            const { success, blocked, message } = response.data;

            if (success) {
                setStatusMessage('OTP Verified! Redirecting...');
                setTimeout(() => navigate('/dashboard'), 1000);
            } else if (blocked) {
                setOtpBlocked(true);
                setError(message);
                setStatusMessage('');
                setLoading(false);
            } else {
                setError(message || 'OTP Verification failed');
                setStatusMessage('');
                setLoading(false);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Connection error');
            setStatusMessage('');
            setLoading(false);
        }
    };

    const handleRetryOtp = async () => {
        setError('');
        setOtpBlocked(false);
        setFormData(prev => ({ ...prev, otp: '' }));

        try {
            await authService.clearOtp();
        } catch (err) {
            console.error('Clear OTP error:', err);
        }
    };

    return (
        <div className="min-vh-100 d-flex align-items-center justify-content-center py-5"
            style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)' }}>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-md-5 col-lg-4">
                        <div className="card card-dark border-0 shadow-lg" style={{ borderTop: '4px solid #3b82f6' }}>
                            <div className="card-body p-4">
                                {/* Header */}
                                <div className="text-center mb-4">
                                    <div className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                                        style={{ width: '60px', height: '60px' }}>
                                        <i className="bi bi-grid-1x2 fs-3 text-white"></i>
                                    </div>
                                    <h2 className="text-gradient fw-bold mb-1">FASIH-SM</h2>
                                    <p className="text-secondary small mb-0">Web Automation Tool</p>
                                </div>

                                {/* Error Alert */}
                                {error && (
                                    <div className="alert alert-danger py-2 d-flex align-items-center gap-2" role="alert">
                                        <i className="bi bi-exclamation-triangle-fill"></i>
                                        <small>{error}</small>
                                    </div>
                                )}

                                {/* Status Message */}
                                {statusMessage && (
                                    <div className="alert alert-info py-2 d-flex align-items-center gap-2" role="alert">
                                        <span className="spinner-border spinner-border-sm"></span>
                                        <small>{statusMessage}</small>
                                    </div>
                                )}

                                {step === 'login' ? (
                                    <form onSubmit={handleLogin}>
                                        <div className="mb-3">
                                            <label className="form-label text-secondary small">Username SSO</label>
                                            <div className="input-group">
                                                <span className="input-group-text bg-dark border-secondary">
                                                    <i className="bi bi-person text-secondary"></i>
                                                </span>
                                                <input
                                                    type="text"
                                                    required
                                                    className="form-control bg-dark text-light border-secondary"
                                                    placeholder="username@bps.go.id"
                                                    value={formData.username}
                                                    onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                                                    disabled={loading}
                                                />
                                            </div>
                                        </div>

                                        <div className="mb-4">
                                            <label className="form-label text-secondary small">Password</label>
                                            <div className="input-group">
                                                <span className="input-group-text bg-dark border-secondary">
                                                    <i className="bi bi-lock text-secondary"></i>
                                                </span>
                                                <input
                                                    type={showPassword ? "text" : "password"}
                                                    required
                                                    className="form-control bg-dark text-light border-secondary"
                                                    placeholder="••••••••"
                                                    value={formData.password}
                                                    onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                                                    disabled={loading}
                                                />
                                                <button
                                                    type="button"
                                                    className="btn btn-outline-secondary border-secondary"
                                                    onClick={() => setShowPassword(!showPassword)}
                                                    tabIndex={-1}
                                                >
                                                    <i className={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}`}></i>
                                                </button>
                                            </div>
                                            {hasSession && (
                                                <small className="text-success">
                                                    <i className="bi bi-check-circle me-1"></i>
                                                    Password auto-filled dari session tersimpan
                                                </small>
                                            )}
                                        </div>

                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="btn btn-primary w-100 d-flex align-items-center justify-content-center gap-2"
                                        >
                                            {loading ? (
                                                <>
                                                    <span className="spinner-border spinner-border-sm"></span>
                                                    {hasSession ? 'Restoring session...' : 'Connecting...'}
                                                </>
                                            ) : (
                                                <>
                                                    Login <i className="bi bi-arrow-right"></i>
                                                </>
                                            )}
                                        </button>
                                    </form>
                                ) : (
                                    <form onSubmit={handleSubmitOtp}>
                                        <div className="text-center mb-4 p-3 bg-dark rounded">
                                            <i className="bi bi-key fs-1 text-primary mb-2 d-block"></i>
                                            <p className="text-secondary small mb-0">
                                                Masukkan kode OTP dari authenticator app
                                            </p>
                                        </div>

                                        {otpBlocked && (
                                            <div className="alert alert-warning py-2 mb-3" role="alert">
                                                <small>
                                                    <i className="bi bi-exclamation-triangle me-1"></i>
                                                    Tutup notifikasi password di browser Chrome, lalu klik Retry.
                                                </small>
                                            </div>
                                        )}

                                        <div className="mb-4">
                                            <label className="form-label text-secondary small">OTP Code</label>
                                            <input
                                                type="text"
                                                required
                                                className="form-control form-control-lg bg-dark text-light border-secondary text-center"
                                                placeholder="000000"
                                                maxLength={6}
                                                value={formData.otp}
                                                onChange={(e) => setFormData({ ...formData, otp: e.target.value.replace(/\D/g, '') })}
                                                disabled={loading}
                                                autoFocus
                                                style={{ letterSpacing: '0.5em', fontSize: '1.5rem' }}
                                            />
                                        </div>

                                        <div className="d-grid gap-2">
                                            {otpBlocked ? (
                                                <button
                                                    type="button"
                                                    onClick={handleRetryOtp}
                                                    className="btn btn-warning d-flex align-items-center justify-content-center gap-2"
                                                >
                                                    <i className="bi bi-arrow-clockwise"></i> Retry Input OTP
                                                </button>
                                            ) : (
                                                <button
                                                    type="submit"
                                                    disabled={loading || formData.otp.length !== 6}
                                                    className="btn btn-primary d-flex align-items-center justify-content-center gap-2"
                                                >
                                                    {loading ? (
                                                        <>
                                                            <span className="spinner-border spinner-border-sm"></span>
                                                            Verifying...
                                                        </>
                                                    ) : (
                                                        <>
                                                            Submit OTP <i className="bi bi-check-lg"></i>
                                                        </>
                                                    )}
                                                </button>
                                            )}

                                            <button
                                                type="button"
                                                onClick={() => { setStep('login'); setError(''); setOtpBlocked(false); }}
                                                className="btn btn-outline-secondary btn-sm"
                                            >
                                                <i className="bi bi-arrow-left me-1"></i> Kembali ke Login
                                            </button>
                                        </div>
                                    </form>
                                )}
                            </div>
                        </div>

                        <p className="text-center text-secondary small mt-3">
                            <i className="bi bi-shield-lock me-1"></i>
                            Session & password disimpan lokal
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
