import { useState } from 'react';
import {
    Box,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography,
    Chip,
    IconButton,
    Stack,
    Divider,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

// 主要な既往歴・怪我のリスト
const COMMON_INJURIES = [
    { label: '膝痛', category: '関節' },
    { label: '腰痛', category: '関節' },
    { label: '肩痛', category: '関節' },
    { label: '首痛', category: '関節' },
    { label: '股関節痛', category: '関節' },
    { label: '足首痛', category: '関節' },
    { label: '手首痛', category: '関節' },
    { label: '肘痛', category: '関節' },
    { label: 'ヘルニア', category: '脊椎' },
    { label: '坐骨神経痛', category: '脊椎' },
    { label: '側弯症', category: '脊椎' },
    { label: '高血圧', category: '内科' },
    { label: '糖尿病', category: '内科' },
    { label: '心疾患', category: '内科' },
    { label: '喘息', category: '内科' },
    { label: '骨粗しょう症', category: '骨' },
    { label: '四十肩・五十肩', category: '関節' },
    { label: '腱鞘炎', category: '筋腱' },
    { label: 'アキレス腱炎', category: '筋腱' },
];

/**
 * ユーザープロフィール入力フォーム
 */
function UserProfileForm({ data, onChange }) {
    const [injuryInput, setInjuryInput] = useState('');

    const handleChange = (field) => (event) => {
        onChange({
            ...data,
            [field]: event.target.value,
        });
    };

    const handleAddInjury = (injury) => {
        const injuryToAdd = typeof injury === 'string' ? injury : injuryInput.trim();
        if (injuryToAdd && !(data.injuries || []).includes(injuryToAdd)) {
            onChange({
                ...data,
                injuries: [...(data.injuries || []), injuryToAdd],
            });
            if (typeof injury !== 'string') {
                setInjuryInput('');
            }
        }
    };

    const handleDeleteInjury = (index) => {
        const newInjuries = data.injuries.filter((_, i) => i !== index);
        onChange({
            ...data,
            injuries: newInjuries,
        });
    };

    const handleToggleCommonInjury = (injury) => {
        const injuries = data.injuries || [];
        if (injuries.includes(injury)) {
            // 既に選択されている場合は削除
            onChange({
                ...data,
                injuries: injuries.filter((i) => i !== injury),
            });
        } else {
            // 選択されていない場合は追加
            onChange({
                ...data,
                injuries: [...injuries, injury],
            });
        }
    };

    const isSelected = (injury) => (data.injuries || []).includes(injury);

    return (
        <Box>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main', fontWeight: 600 }}>
                👤 ユーザープロフィール
            </Typography>

            <Stack spacing={3}>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <TextField
                        label="年齢"
                        type="number"
                        value={data.age || ''}
                        onChange={handleChange('age')}
                        inputProps={{ min: 10, max: 100 }}
                        fullWidth
                        required
                    />

                    <FormControl fullWidth required>
                        <InputLabel>性別</InputLabel>
                        <Select
                            value={data.gender || ''}
                            label="性別"
                            onChange={handleChange('gender')}
                        >
                            <MenuItem value="男性">男性</MenuItem>
                            <MenuItem value="女性">女性</MenuItem>
                        </Select>
                    </FormControl>
                </Stack>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <TextField
                        label="身長 (cm)"
                        type="number"
                        value={data.height_cm || ''}
                        onChange={handleChange('height_cm')}
                        inputProps={{ min: 100, max: 250, step: 0.1 }}
                        fullWidth
                        required
                    />

                    <FormControl fullWidth required>
                        <InputLabel>トレーニング経験</InputLabel>
                        <Select
                            value={data.training_experience || ''}
                            label="トレーニング経験"
                            onChange={handleChange('training_experience')}
                        >
                            <MenuItem value="初級者">初級者</MenuItem>
                            <MenuItem value="中級者">中級者</MenuItem>
                            <MenuItem value="上級者">上級者</MenuItem>
                        </Select>
                    </FormControl>
                </Stack>

                <Box>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        🩺 既往歴・怪我
                    </Typography>

                    {/* 主要な既往歴の選択チップ */}
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                        よくある項目をクリックで選択できます
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                        {/* 関節系 */}
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            関節・痛み
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1.5 }}>
                            {COMMON_INJURIES.filter(i => i.category === '関節').map((injury) => (
                                <Chip
                                    key={injury.label}
                                    label={injury.label}
                                    onClick={() => handleToggleCommonInjury(injury.label)}
                                    color={isSelected(injury.label) ? 'primary' : 'default'}
                                    variant={isSelected(injury.label) ? 'filled' : 'outlined'}
                                    size="small"
                                    sx={{
                                        cursor: 'pointer',
                                        transition: 'all 0.2s',
                                        '&:hover': {
                                            transform: 'scale(1.05)',
                                        }
                                    }}
                                />
                            ))}
                        </Box>

                        {/* 脊椎系 */}
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            脊椎・神経
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1.5 }}>
                            {COMMON_INJURIES.filter(i => i.category === '脊椎').map((injury) => (
                                <Chip
                                    key={injury.label}
                                    label={injury.label}
                                    onClick={() => handleToggleCommonInjury(injury.label)}
                                    color={isSelected(injury.label) ? 'primary' : 'default'}
                                    variant={isSelected(injury.label) ? 'filled' : 'outlined'}
                                    size="small"
                                    sx={{
                                        cursor: 'pointer',
                                        transition: 'all 0.2s',
                                        '&:hover': {
                                            transform: 'scale(1.05)',
                                        }
                                    }}
                                />
                            ))}
                        </Box>

                        {/* 内科系 */}
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            内科疾患
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1.5 }}>
                            {COMMON_INJURIES.filter(i => i.category === '内科').map((injury) => (
                                <Chip
                                    key={injury.label}
                                    label={injury.label}
                                    onClick={() => handleToggleCommonInjury(injury.label)}
                                    color={isSelected(injury.label) ? 'warning' : 'default'}
                                    variant={isSelected(injury.label) ? 'filled' : 'outlined'}
                                    size="small"
                                    sx={{
                                        cursor: 'pointer',
                                        transition: 'all 0.2s',
                                        '&:hover': {
                                            transform: 'scale(1.05)',
                                        }
                                    }}
                                />
                            ))}
                        </Box>

                        {/* その他 */}
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            骨・筋腱
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {COMMON_INJURIES.filter(i => i.category === '骨' || i.category === '筋腱').map((injury) => (
                                <Chip
                                    key={injury.label}
                                    label={injury.label}
                                    onClick={() => handleToggleCommonInjury(injury.label)}
                                    color={isSelected(injury.label) ? 'primary' : 'default'}
                                    variant={isSelected(injury.label) ? 'filled' : 'outlined'}
                                    size="small"
                                    sx={{
                                        cursor: 'pointer',
                                        transition: 'all 0.2s',
                                        '&:hover': {
                                            transform: 'scale(1.05)',
                                        }
                                    }}
                                />
                            ))}
                        </Box>
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    {/* カスタム入力 */}
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                        上記にない場合は手動で追加
                    </Typography>
                    <Stack direction="row" spacing={1} alignItems="center">
                        <TextField
                            placeholder="その他の既往歴を入力"
                            value={injuryInput}
                            onChange={(e) => setInjuryInput(e.target.value)}
                            size="small"
                            sx={{ flexGrow: 1 }}
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    handleAddInjury();
                                }
                            }}
                        />
                        <IconButton color="primary" onClick={() => handleAddInjury()}>
                            <AddIcon />
                        </IconButton>
                    </Stack>

                    {/* 選択済み表示 */}
                    {(data.injuries || []).length > 0 && (
                        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                                選択中の既往歴（{data.injuries.length}件）
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                {data.injuries.map((injury, index) => (
                                    <Chip
                                        key={index}
                                        label={injury}
                                        onDelete={() => handleDeleteInjury(index)}
                                        color="secondary"
                                        variant="filled"
                                    />
                                ))}
                            </Box>
                        </Box>
                    )}
                </Box>
            </Stack>
        </Box>
    );
}

export default UserProfileForm;
