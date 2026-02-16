import {
    Backdrop,
    CircularProgress,
    Typography,
    Box,
} from '@mui/material';

/**
 * ローディングオーバーレイコンポーネント
 */
function LoadingOverlay({ open, message = '処理中...' }) {
    return (
        <Backdrop
            sx={{
                color: '#fff',
                zIndex: (theme) => theme.zIndex.drawer + 1,
                flexDirection: 'column',
                gap: 3,
                background: 'rgba(0, 0, 0, 0.8)',
            }}
            open={open}
        >
            <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2
            }}>
                <CircularProgress color="primary" size={60} thickness={4} />
                <Typography variant="h6" sx={{ fontWeight: 500 }}>
                    {message}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    AIがあなたのデータを分析中です...
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.6 }}>
                    30秒〜1分程度かかる場合があります
                </Typography>
            </Box>
        </Backdrop>
    );
}

export default LoadingOverlay;
