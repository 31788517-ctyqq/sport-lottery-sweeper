import sys
sys.path.insert(0, '.')
import traceback

models_to_test = [
    "backend.models.match.Match",
    "backend.models.user.User",
    "backend.models.admin_user.AdminUser",
    "backend.models.data.AdminData",
    "backend.models.data_review.DataReview",
    "backend.models.intelligence.Intelligence",
    "backend.models.venues.Venue",
    "backend.models.odds.Odds",
    "backend.models.predictions.Prediction",
    "backend.models.draw_feature.DrawFeature",
    "backend.models.draw_training_job.DrawTrainingJob",
    "backend.models.draw_model_version.DrawModelVersion",
    "backend.models.draw_prediction_result.DrawPredictionResult",
    "backend.models.data_sources.DataSource",
    "backend.models.odds_companies.OddsCompany",
    "backend.models.sp_records.SPRecord",
    "backend.models.sp_modification_logs.SPModificationLog",
]

success_count = 0
for model_path in models_to_test:
    try:
        exec(f"from {model_path} import *")
        print(f"✓ {model_path}")
        success_count += 1
    except Exception as e:
        print(f"✗ {model_path}: {e}")
        traceback.print_exc()

print(f"\n导入成功: {success_count}/{len(models_to_test)}")