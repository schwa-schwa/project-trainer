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
 * 好み・制約設定フォーム
 */
function PreferencesForm({ data, onChange }) {
    const handleChange = (field) => (event) => {
        onChange({
            ...data,
            [field]: event.target.value,
        });
    };

    return (
        <Box>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 600 }}>
                ⚙️ 好み・制約
            </Typography>

            <Stack spacing={3}>
                <FormControl fullWidth>
                    <InputLabel>トレーニング環境</InputLabel>
                    <Select
                        value={data.environment || 'home'}
                        label="トレーニング環境"
                        onChange={handleChange('environment')}
                    >
                        <MenuItem value="home">自宅トレーニング</MenuItem>
                        <MenuItem value="gym">ジムトレーニング</MenuItem>
                    </Select>
                </FormControl>

                <FormControl fullWidth>
                    <InputLabel>一日のトレーニング時間</InputLabel>
                    <Select
                        value={data.training_time_minutes || '60'}
                        label="一日のトレーニング時間"
                        onChange={handleChange('training_time_minutes')}
                    >
                        <MenuItem value="5">5分</MenuItem>
                        <MenuItem value="10">10分</MenuItem>
                        <MenuItem value="15">15分</MenuItem>
                        <MenuItem value="30">30分</MenuItem>
                        <MenuItem value="45">45分</MenuItem>
                        <MenuItem value="60">60分</MenuItem>
                        <MenuItem value="90">90分</MenuItem>
                        <MenuItem value="120">120分</MenuItem>
                    </Select>
                </FormControl>

                <TextField
                    label="利用可能な器具"
                    placeholder="例: ダンベル、チューブ、ヨガマット"
                    value={data.equipment || ''}
                    onChange={handleChange('equipment')}
                    fullWidth
                    multiline
                    rows={2}
                />

                <TextField
                    label="スケジュールに関する注記"
                    placeholder="例: 朝の時間しか取れない、平日のみ可能"
                    value={data.schedule_notes || ''}
                    onChange={handleChange('schedule_notes')}
                    fullWidth
                    multiline
                    rows={2}
                />

                <TextField
                    label="その他の要望"
                    placeholder="例: 短時間で完了したい、静かな運動がいい"
                    value={data.specific_requests || ''}
                    onChange={handleChange('specific_requests')}
                    fullWidth
                    multiline
                    rows={2}
                />
            </Stack>
        </Box>
    );
}

export default PreferencesForm;
