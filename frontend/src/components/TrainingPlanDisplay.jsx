import { Fragment } from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Chip,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Divider,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import BuildIcon from '@mui/icons-material/Build';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

/**
 * トレーニングプラン表示コンポーネント
 */
function TrainingPlanDisplay({ plan }) {
    if (!plan) return null;

    return (
        <Box>
            <Typography variant="h5" gutterBottom sx={{
                color: 'primary.main',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: 1
            }}>
                🏋️ トレーニングプラン
            </Typography>

            {/* 分割法 */}
            <Card elevation={3} sx={{ mb: 3, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }} className="no-print">
                <CardContent sx={{ color: 'white' }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                        分割法: {plan.split_method}
                    </Typography>
                    <Typography variant="body1" sx={{ opacity: 0.95 }}>
                        {plan.split_rationale}
                    </Typography>
                </CardContent>
            </Card>

            {/* 週間スケジュール */}
            <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 2 }}>
                📅 週間スケジュール
            </Typography>

            {plan.weekly_schedule && plan.weekly_schedule.map((day, dayIndex) => (
                <Accordion key={dayIndex} defaultExpanded={dayIndex === 0} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Chip
                                label={day.day_label}
                                color="primary"
                                size="small"
                                sx={{ fontWeight: 600 }}
                            />
                            <Typography sx={{ fontWeight: 500 }}>{day.focus}</Typography>
                        </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                        <TableContainer component={Paper} variant="outlined">
                            <Table size="small">
                                <TableHead>
                                    <TableRow sx={{ backgroundColor: 'primary.light' }}>
                                        <TableCell sx={{ color: 'white', fontWeight: 600 }}>部位</TableCell>
                                        <TableCell sx={{ color: 'white', fontWeight: 600 }}>トレーニング内容</TableCell>
                                        <TableCell sx={{ color: 'white', fontWeight: 600 }} align="center">組数</TableCell>
                                        <TableCell sx={{ color: 'white', fontWeight: 600 }} align="center">回数</TableCell>
                                        <TableCell sx={{ color: 'white', fontWeight: 600 }} align="center">休憩時間</TableCell>
                                        <TableCell sx={{ color: 'white', fontWeight: 600 }}>メモ</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {day.exercises && day.exercises.map((exercise, exIndex) => (
                                        <Fragment key={exIndex}>
                                            <TableRow hover>
                                                <TableCell>
                                                    <Chip
                                                        label={exercise.target_area}
                                                        size="small"
                                                        variant="outlined"
                                                        color="secondary"
                                                    />
                                                </TableCell>
                                                <TableCell sx={{ fontWeight: 500 }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <FitnessCenterIcon fontSize="small" color="action" />
                                                        {exercise.exercise_name}
                                                    </Box>
                                                </TableCell>
                                                <TableCell align="center">{exercise.sets}</TableCell>
                                                <TableCell align="center">{exercise.reps}</TableCell>
                                                <TableCell align="center" sx={{ color: 'text.secondary' }}>
                                                    {exercise.interval_seconds ? `${exercise.interval_seconds}秒` : '60秒'}
                                                </TableCell>
                                                <TableCell sx={{ color: 'text.secondary', fontSize: '0.875rem' }}>
                                                    {exercise.notes || '-'}
                                                </TableCell>
                                            </TableRow>
                                            {exercise.instructions && exercise.instructions.length > 0 && (
                                                <TableRow key={`${exIndex}-instructions`}>
                                                    <TableCell colSpan={6} sx={{ backgroundColor: 'grey.50', py: 1 }}>
                                                        <Box sx={{ pl: 2 }}>
                                                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                                                                📋 動作手順:
                                                            </Typography>
                                                            <List dense sx={{ py: 0 }}>
                                                                {exercise.instructions.map((step, stepIndex) => (
                                                                    <ListItem key={stepIndex} sx={{ py: 0.25 }}>
                                                                        <ListItemText
                                                                            primary={`${stepIndex + 1}. ${step}`}
                                                                            primaryTypographyProps={{ variant: 'body2', color: 'text.secondary' }}
                                                                        />
                                                                    </ListItem>
                                                                ))}
                                                            </List>
                                                        </Box>
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </Fragment>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </AccordionDetails>
                </Accordion>
            ))}

            {/* 修正事項 */}
            {plan.modifications && plan.modifications.length > 0 && (
                <Card elevation={2} sx={{ mt: 3, borderLeft: '4px solid', borderColor: 'warning.main' }} className="no-print">
                    <CardContent>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <BuildIcon color="warning" /> リスク対応の修正
                        </Typography>
                        <List dense>
                            {plan.modifications.map((mod, index) => (
                                <ListItem key={index}>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="warning" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText primary={mod} />
                                </ListItem>
                            ))}
                        </List>
                    </CardContent>
                </Card>
            )}

            {/* 優先ポイント */}
            {plan.priority_points && plan.priority_points.length > 0 && (
                <Card elevation={2} sx={{ mt: 3, borderLeft: '4px solid', borderColor: 'success.main' }} className="no-print">
                    <CardContent>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <TipsAndUpdatesIcon color="success" /> 優先的に取り組むポイント
                        </Typography>
                        <List dense>
                            {plan.priority_points.map((point, index) => (
                                <ListItem key={index}>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="success" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText primary={point} />
                                </ListItem>
                            ))}
                        </List>
                    </CardContent>
                </Card>
            )}

            {/* 栄養アドバイス */}
            {plan.nutrition_tips && plan.nutrition_tips.length > 0 && (
                <Card elevation={2} sx={{ mt: 3, borderLeft: '4px solid', borderColor: 'info.main' }} className="no-print">
                    <CardContent>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <RestaurantIcon color="info" /> 栄養アドバイス
                        </Typography>
                        <List dense>
                            {plan.nutrition_tips.map((tip, index) => (
                                <ListItem key={index}>
                                    <ListItemIcon>
                                        <CheckCircleIcon color="info" fontSize="small" />
                                    </ListItemIcon>
                                    <ListItemText primary={tip} />
                                </ListItem>
                            ))}
                        </List>
                    </CardContent>
                </Card>
            )}
        </Box>
    );
}

export default TrainingPlanDisplay;
