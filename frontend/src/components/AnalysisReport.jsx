import {
    Box,
    Typography,
    Card,
    CardContent,
    Chip,
    Grid,
    Divider,
} from '@mui/material';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import WarningIcon from '@mui/icons-material/Warning';
import BalanceIcon from '@mui/icons-material/Balance';

/**
 * 分析レポート表示コンポーネント
 */
function AnalysisReport({ report }) {
    if (!report) return null;

    return (
        <Box>
            <Typography variant="h5" gutterBottom sx={{
                color: 'primary.main',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: 1
            }}>
                📋 分析レポート
            </Typography>

            <Grid container spacing={3}>
                {/* 体型評価 */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card elevation={3} sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                        <CardContent sx={{ color: 'white' }}>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <FitnessCenterIcon /> 体組成評価
                            </Typography>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>体型タイプ</Typography>
                                <Typography variant="h5" sx={{ fontWeight: 600 }}>{report.body_type}</Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>体脂肪率評価</Typography>
                                <Typography>{report.body_fat_evaluation}</Typography>
                            </Box>

                            <Box>
                                <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>骨格筋量評価</Typography>
                                <Typography>{report.skeletal_muscle_evaluation}</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* バランス評価 */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card elevation={3} sx={{ height: '100%', background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' }}>
                        <CardContent sx={{ color: 'white' }}>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <BalanceIcon /> バランス評価
                            </Typography>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>腕の左右バランス</Typography>
                                <Typography>{report.arm_balance}</Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>脚の左右バランス</Typography>
                                <Typography>{report.leg_balance}</Typography>
                            </Box>

                            <Box>
                                <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>上下肢バランス</Typography>
                                <Typography>{report.upper_lower_balance}</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* リスク要因 */}
                <Grid size={{ xs: 12 }}>
                    <Card elevation={3}>
                        <CardContent>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, color: 'warning.main' }}>
                                <WarningIcon /> リスク要因・注意点
                            </Typography>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="text.secondary">リスク要因</Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                                    {report.risk_factors && report.risk_factors.length > 0 ? (
                                        report.risk_factors.map((risk, index) => (
                                            <Chip key={index} label={risk} color="warning" variant="outlined" />
                                        ))
                                    ) : (
                                        <Typography color="text.secondary">特になし</Typography>
                                    )}
                                </Box>
                            </Box>

                            <Divider sx={{ my: 2 }} />

                            <Box>
                                <Typography variant="subtitle2" color="text.secondary">懸念事項</Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                                    {report.concerns && report.concerns.length > 0 ? (
                                        report.concerns.map((concern, index) => (
                                            <Chip key={index} label={concern} color="info" variant="outlined" />
                                        ))
                                    ) : (
                                        <Typography color="text.secondary">特になし</Typography>
                                    )}
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}

export default AnalysisReport;
