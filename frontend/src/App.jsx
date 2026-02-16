import { useState } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Box,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Alert,
  Snackbar,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import PrintIcon from '@mui/icons-material/Print';

import {
  UserProfileForm,
  InBodyDataForm,
  GoalForm,
  PreferencesForm,
  AnalysisReport,
  TrainingPlanDisplay,
  LoadingOverlay,
} from './components';
import { generateTrainingPlan } from './services/api';

// カスタムテーマ
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6366f1', // Indigo
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#ec4899', // Pink
      light: '#f472b6',
      dark: '#db2777',
    },
    success: {
      main: '#10b981',
    },
    warning: {
      main: '#f59e0b',
    },
    info: {
      main: '#06b6d4',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Noto Sans JP", sans-serif',
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          padding: '10px 24px',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        },
      },
    },
  },
});

const steps = ['プロフィール', 'InBodyデータ', '目標設定', '好み'];

// 初期データ
const initialFormData = {
  user_profile: {
    age: '',
    gender: '',
    height_cm: '',
    training_experience: '',
    injuries: [],
  },
  inbody_metrics: {
    weight_kg: '',
    muscle_mass_kg: '',
    skeletal_muscle_mass_kg: '',
    body_fat_percent: '',
    segmental_lean: {
      right_arm: '',
      left_arm: '',
      trunk: '',
      right_leg: '',
      left_leg: '',
    },
  },
  goal: {
    type: '',
    days_per_week: '',
  },
  preferences: {
    environment: 'home',
    training_time_minutes: '60',
    equipment: '',
    schedule_notes: '',
    specific_requests: '',
  },
};

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState(initialFormData);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResult, setShowResult] = useState(false);

  const handleNext = () => {
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setFormData(initialFormData);
    setResult(null);
    setShowResult(false);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await generateTrainingPlan(formData);
      setResult(response);
      setShowResult(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (section) => (data) => {
    setFormData((prev) => ({
      ...prev,
      [section]: data,
    }));
  };

  // 各ステップのバリデーション
  const validateStep = (step) => {
    switch (step) {
      case 0: { // プロフィール
        const profile = formData.user_profile;
        return !!(
          profile.age &&
          profile.gender &&
          profile.height_cm &&
          profile.training_experience
        );
      }
      case 1: { // InBodyデータ
        const inbody = formData.inbody_metrics;
        const segmental = inbody.segmental_lean || {};
        return !!(
          inbody.weight_kg &&
          inbody.muscle_mass_kg &&
          inbody.skeletal_muscle_mass_kg &&
          inbody.body_fat_percent &&
          segmental.right_arm &&
          segmental.left_arm &&
          segmental.trunk &&
          segmental.right_leg &&
          segmental.left_leg
        );
      }
      case 2: // 目標設定
        return !!formData.goal.type;
      case 3: // 好み（任意なので常にtrue）
        return true;
      default:
        return true;
    }
  };

  const isCurrentStepValid = validateStep(activeStep);

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <UserProfileForm
            data={formData.user_profile}
            onChange={updateFormData('user_profile')}
          />
        );
      case 1:
        return (
          <InBodyDataForm
            data={formData.inbody_metrics}
            onChange={updateFormData('inbody_metrics')}
          />
        );
      case 2:
        return (
          <GoalForm
            data={formData.goal}
            onChange={updateFormData('goal')}
          />
        );
      case 3:
        return (
          <PreferencesForm
            data={formData.preferences}
            onChange={updateFormData('preferences')}
          />
        );
      default:
        return null;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LoadingOverlay open={loading} message="トレーニングプランを生成中..." />

      <Box
        className="page-background"
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          py: 4,
        }}
      >
        <Container maxWidth="lg">
          {/* ヘッダー */}
          <Box sx={{ textAlign: 'center', mb: 4, color: 'white' }} className="no-print">
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
              🏋️ Project Trainer
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9 }}>
              AIがあなた専用のトレーニングメニューを作成します
            </Typography>
          </Box>

          {!showResult ? (
            /* 入力フォーム */
            <Paper elevation={8} sx={{ p: 4, borderRadius: 3 }}>
              <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
                {steps.map((label) => (
                  <Step key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>

              <Box sx={{ minHeight: 400, py: 2 }}>
                {renderStepContent(activeStep)}
              </Box>

              <Divider sx={{ my: 3 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Button
                  disabled={activeStep === 0}
                  onClick={handleBack}
                  variant="outlined"
                >
                  戻る
                </Button>

                {activeStep === steps.length - 1 ? (
                  <Button
                    variant="contained"
                    onClick={handleSubmit}
                    endIcon={<SendIcon />}
                    size="large"
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                      },
                    }}
                  >
                    プランを生成する
                  </Button>
                ) : (
                  <Button variant="contained" onClick={handleNext} disabled={!isCurrentStepValid}>
                    次へ
                  </Button>
                )}
              </Box>
            </Paper>
          ) : (
            /* 結果表示 */
            <Box>
              <Paper elevation={8} sx={{ p: 4, borderRadius: 3, mb: 3 }} className="no-print">
                <AnalysisReport report={result?.analysis_report} />
              </Paper>

              <Paper elevation={8} sx={{ p: 4, borderRadius: 3, mb: 3 }}>
                <TrainingPlanDisplay plan={result?.training_plan} />
              </Paper>

              <Box sx={{ textAlign: 'center', display: 'flex', justifyContent: 'center', gap: 2 }} className="no-print">
                <Button
                  variant="contained"
                  onClick={handlePrint}
                  startIcon={<PrintIcon />}
                  size="large"
                  sx={{
                    background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #0e8c82 0%, #2ed872 100%)',
                    },
                  }}
                >
                  印刷する
                </Button>
                <Button
                  variant="contained"
                  onClick={handleReset}
                  startIcon={<RestartAltIcon />}
                  size="large"
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                    },
                  }}
                >
                  新しいプランを作成
                </Button>
              </Box>
            </Box>
          )}
        </Container>
      </Box>

      {/* エラー通知 */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        className="no-print"
      >
        <Alert severity="error" onClose={() => setError(null)} sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;
