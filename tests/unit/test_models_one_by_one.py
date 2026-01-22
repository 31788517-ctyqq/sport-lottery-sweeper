import sys, traceback
sys.path.insert(0, '.')

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

for model_path in models_to_test:
    try:
        # 分割模块和类名
        module_name, class_name = model_path.rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"✓ {model_path}")
    except Exception as e:
        print(f"✗ {model_path}: {e}")
        traceback.print_exc()

print("\nDone.")