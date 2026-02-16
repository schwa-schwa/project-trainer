import {
    Box,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography,
    Stack,
} from '@mui/material';

/**
 * 目標設定フォーム
 */
function GoalForm({ data, onChange }) {
    const handleChange = (field) => (event) => {
        onChange({
            ...data,
            [field]: event.target.value,
        });
    };

    return (
        <Box>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 600 }}>
                🎯 目標設定
            </Typography>

            <Stack spacing={3}>
                <FormControl fullWidth required>
                    <InputLabel>目標タイプ</InputLabel>
                    <Select
                        value={data.type || ''}
                        label="目標タイプ"
                        onChange={handleChange('type')}
                    >
                        <MenuItem value="体重を減らしたい">体重を減らしたい</MenuItem>
                        <MenuItem value="筋肉を増やしたい">筋肉を増やしたい</MenuItem>
                        <MenuItem value="体を鍛え直したい">体を鍛え直したい（減量＋筋力）</MenuItem>
                        <MenuItem value="健康を維持したい">健康を維持したい</MenuItem>
                    </Select>
                </FormControl>

                <FormControl fullWidth>
                    <InputLabel>週のトレーニング日数</InputLabel>
                    <Select
                        value={data.days_per_week || ''}
                        label="週のトレーニング日数"
                        onChange={handleChange('days_per_week')}
                    >
                        <MenuItem value="おまかせ">おまかせ</MenuItem>
                        <MenuItem value="2">週2日</MenuItem>
                        <MenuItem value="3">週3日</MenuItem>
                        <MenuItem value="4">週4日</MenuItem>
                        <MenuItem value="5">週5日</MenuItem>
                        <MenuItem value="6">週6日</MenuItem>
                    </Select>
                </FormControl>
            </Stack>
        </Box>
    );
}

export default GoalForm;
