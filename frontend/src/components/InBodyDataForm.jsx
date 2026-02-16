import { useState, useRef } from 'react';
import {
    Box,
    TextField,
    Typography,
    Stack,
    Divider,
    Button,
    Card,
    CardContent,
    Alert,
    CircularProgress,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    IconButton,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import CloseIcon from '@mui/icons-material/Close';
import FlipCameraIosIcon from '@mui/icons-material/FlipCameraIos';
import { extractInBodyDataFromImage } from '../services/api';

/**
 * InBody測定データ入力フォーム
 */
function InBodyDataForm({ data, onChange }) {
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState(null);
    const [uploadError, setUploadError] = useState(null);
    const [isCameraOpen, setIsCameraOpen] = useState(false);
    const [cameraError, setCameraError] = useState(null);
    const [isMirrored, setIsMirrored] = useState(false);

    const fileInputRef = useRef(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);

    const handleChange = (field) => (event) => {
        onChange({
            ...data,
            [field]: parseFloat(event.target.value) || '',
        });
    };

    const handleSegmentalChange = (field) => (event) => {
        onChange({
            ...data,
            segmental_lean: {
                ...(data.segmental_lean || {}),
                [field]: parseFloat(event.target.value) || '',
            },
        });
    };

    const processImage = async (file) => {
        setUploading(true);
        setUploadError(null);
        setUploadResult(null);

        try {
            const result = await extractInBodyDataFromImage(file);
            setUploadResult(result);

            // 抽出されたデータをフォームに適用
            const newData = { ...data };

            if (result.weight_kg != null) newData.weight_kg = result.weight_kg;
            if (result.muscle_mass_kg != null) newData.muscle_mass_kg = result.muscle_mass_kg;
            if (result.skeletal_muscle_mass_kg != null) newData.skeletal_muscle_mass_kg = result.skeletal_muscle_mass_kg;
            if (result.body_fat_percent != null) newData.body_fat_percent = result.body_fat_percent;

            if (result.segmental_lean) {
                newData.segmental_lean = {
                    ...(data.segmental_lean || {}),
                };
                if (result.segmental_lean.right_arm != null) newData.segmental_lean.right_arm = result.segmental_lean.right_arm;
                if (result.segmental_lean.left_arm != null) newData.segmental_lean.left_arm = result.segmental_lean.left_arm;
                if (result.segmental_lean.trunk != null) newData.segmental_lean.trunk = result.segmental_lean.trunk;
                if (result.segmental_lean.right_leg != null) newData.segmental_lean.right_leg = result.segmental_lean.right_leg;
                if (result.segmental_lean.left_leg != null) newData.segmental_lean.left_leg = result.segmental_lean.left_leg;
            }

            onChange(newData);
        } catch (error) {
            setUploadError(error.message);
        } finally {
            setUploading(false);
        }
    };

    const handleFileSelect = (event) => {
        const file = event.target.files?.[0];
        if (!file) return;
        processImage(file);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const startCamera = async () => {
        setIsCameraOpen(true);
        setCameraError(null);
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' }
            });
            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
        } catch (err) {
            setCameraError('カメラへのアクセスを許可してください。');
            console.error(err);
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setIsCameraOpen(false);
    };

    const toggleMirror = () => {
        setIsMirrored(prev => !prev);
    };

    const capturePhoto = () => {
        if (videoRef.current && canvasRef.current) {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');

            // OCRのため、プレビューが反転していても撮影画像は正像でキャプチャする
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob((blob) => {
                if (blob) {
                    const file = new File([blob], "captured_inbody.jpg", { type: "image/jpeg" });
                    processImage(file);
                }
            }, 'image/jpeg', 0.9);

            stopCamera();
        }
    };

    const getConfidenceColor = (confidence) => {
        switch (confidence) {
            case 'high': return 'success';
            case 'medium': return 'warning';
            case 'low': return 'error';
            default: return 'default';
        }
    };

    const getConfidenceLabel = (confidence) => {
        switch (confidence) {
            case 'high': return '高精度';
            case 'medium': return '中精度';
            case 'low': return '低精度';
            default: return '不明';
        }
    };

    return (
        <Box>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 600 }}>
                📊 InBody測定データ
            </Typography>

            {/* 画像入力セクション */}
            <Card
                elevation={2}
                sx={{
                    mb: 3,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white'
                }}
            >
                <CardContent>
                    <Typography variant="subtitle1" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AutoFixHighIcon /> AIで画像から自動入力
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, opacity: 0.9 }}>
                        InBodyの結果シートを撮影または画像をアップロードすると、
                        AIが自動的にデータを読み取ります。
                    </Typography>

                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                        {/* 撮影ボタン */}
                        <Button
                            variant="contained"
                            onClick={startCamera}
                            startIcon={<CameraAltIcon />}
                            disabled={uploading}
                            sx={{
                                bgcolor: 'rgba(255,255,255,0.2)',
                                '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                                color: 'white',
                                flexGrow: 1
                            }}
                        >
                            今すぐ撮影する
                        </Button>

                        {/* アップロードボタン */}
                        <input
                            type="file"
                            accept="image/jpeg,image/png,image/webp,image/heic"
                            onChange={handleFileSelect}
                            ref={fileInputRef}
                            style={{ display: 'none' }}
                            id="inbody-image-upload"
                        />
                        <label htmlFor="inbody-image-upload" style={{ flexGrow: 1 }}>
                            <Button
                                variant="contained"
                                component="span"
                                startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
                                disabled={uploading}
                                sx={{
                                    bgcolor: 'rgba(255,255,255,0.2)',
                                    '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                                    color: 'white',
                                    width: '100%'
                                }}
                            >
                                {uploading ? '解析中...' : 'ファイルを選択'}
                            </Button>
                        </label>
                    </Stack>
                </CardContent>
            </Card>

            {/* カメラダイアログ */}
            <Dialog
                open={isCameraOpen}
                onClose={stopCamera}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">InBodyを撮影</Typography>
                    <Box>
                        <IconButton onClick={toggleMirror} title="画像を反転" sx={{ mr: 1 }}>
                            <FlipCameraIosIcon color={isMirrored ? 'primary' : 'inherit'} />
                        </IconButton>
                        <IconButton onClick={stopCamera}>
                            <CloseIcon />
                        </IconButton>
                    </Box>
                </DialogTitle>
                <DialogContent dividers sx={{ p: 0, overflow: 'hidden', bgcolor: 'black', display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '300px' }}>
                    {cameraError ? (
                        <Typography color="error" sx={{ p: 3 }}>{cameraError}</Typography>
                    ) : (
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            style={{
                                width: '100%',
                                maxHeight: '70vh',
                                objectFit: 'contain',
                                transform: isMirrored ? 'scaleX(-1)' : 'none'
                            }}
                        />
                    )}
                    <canvas ref={canvasRef} style={{ display: 'none' }} />
                </DialogContent>
                <DialogActions sx={{ p: 2, justifyContent: 'center' }}>
                    {!cameraError && (
                        <Button
                            variant="contained"
                            size="large"
                            startIcon={<CameraAltIcon />}
                            onClick={capturePhoto}
                            sx={{ borderRadius: 10, px: 4, py: 1.5 }}
                        >
                            シャッター
                        </Button>
                    )}
                </DialogActions>
            </Dialog>

            {/* アップロード結果の表示 */}
            {uploadResult && (
                <Alert
                    severity="success"
                    sx={{ mb: 2 }}
                    icon={<CheckCircleIcon />}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <span>画像からデータを抽出しました</span>
                        <Chip
                            label={getConfidenceLabel(uploadResult.confidence)}
                            color={getConfidenceColor(uploadResult.confidence)}
                            size="small"
                        />
                    </Box>
                    {uploadResult.notes && (
                        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                            {uploadResult.notes}
                        </Typography>
                    )}
                </Alert>
            )}

            {uploadError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {uploadError}
                </Alert>
            )}

            <Stack spacing={3}>
                {/* 基本データ */}
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <TextField
                        label="体重 (kg)"
                        type="number"
                        value={data.weight_kg || ''}
                        onChange={handleChange('weight_kg')}
                        inputProps={{ min: 30, max: 200, step: 0.1 }}
                        fullWidth
                        required
                    />
                    <TextField
                        label="筋肉量 (kg)"
                        type="number"
                        value={data.muscle_mass_kg || ''}
                        onChange={handleChange('muscle_mass_kg')}
                        inputProps={{ min: 10, max: 100, step: 0.1 }}
                        fullWidth
                        required
                    />
                </Stack>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <TextField
                        label="骨格筋量 (kg)"
                        type="number"
                        value={data.skeletal_muscle_mass_kg || ''}
                        onChange={handleChange('skeletal_muscle_mass_kg')}
                        inputProps={{ min: 5, max: 60, step: 0.1 }}
                        fullWidth
                        required
                    />
                    <TextField
                        label="体脂肪率 (%)"
                        type="number"
                        value={data.body_fat_percent || ''}
                        onChange={handleChange('body_fat_percent')}
                        inputProps={{ min: 3, max: 60, step: 0.1 }}
                        fullWidth
                        required
                    />
                </Stack>

                <Divider sx={{ my: 1 }} />

                {/* 部位別骨格筋量 */}
                <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                    🦴 部位別骨格筋量
                </Typography>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <TextField
                        label="左腕 (kg)"
                        type="number"
                        value={data.segmental_lean?.left_arm || ''}
                        onChange={handleSegmentalChange('left_arm')}
                        inputProps={{ min: 0, max: 10, step: 0.01 }}
                        fullWidth
                        required
                    />
                    <TextField
                        label="右腕 (kg)"
                        type="number"
                        value={data.segmental_lean?.right_arm || ''}
                        onChange={handleSegmentalChange('right_arm')}
                        inputProps={{ min: 0, max: 10, step: 0.01 }}
                        fullWidth
                        required
                    />
                </Stack>

                <TextField
                    label="体幹 (kg)"
                    type="number"
                    value={data.segmental_lean?.trunk || ''}
                    onChange={handleSegmentalChange('trunk')}
                    inputProps={{ min: 0, max: 40, step: 0.1 }}
                    fullWidth
                    required
                />

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <TextField
                        label="左脚 (kg)"
                        type="number"
                        value={data.segmental_lean?.left_leg || ''}
                        onChange={handleSegmentalChange('left_leg')}
                        inputProps={{ min: 0, max: 20, step: 0.01 }}
                        fullWidth
                        required
                    />
                    <TextField
                        label="右脚 (kg)"
                        type="number"
                        value={data.segmental_lean?.right_leg || ''}
                        onChange={handleSegmentalChange('right_leg')}
                        inputProps={{ min: 0, max: 20, step: 0.01 }}
                        fullWidth
                        required
                    />
                </Stack>
            </Stack>
        </Box>
    );
}

export default InBodyDataForm;
