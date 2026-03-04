from __future__ import annotations

from datetime import datetime
from pathlib import Path
import math
import pickle
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy.orm import Session

from backend.models.draw_feature import DrawFeature
from backend.models.draw_training_job import DrawTrainingJob
from backend.models.match import Match

try:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return default
        return float(value)
    text = str(value).strip()
    if not text:
        return default
    text = text.replace("＋", "+").replace("－", "-")
    if text in {"平手", "平/半", "平手/半球", "0", "-0", "+0"}:
        return 0.0
    if "/" in text:
        parts = [_to_float(part, default=default) for part in text.split("/") if str(part).strip()]
        if parts:
            return float(sum(parts) / len(parts))
    try:
        return float(text)
    except ValueError:
        sign = -1.0 if text.startswith("-") else 1.0
        digits = []
        has_dot = False
        for ch in text:
            if ch.isdigit():
                digits.append(ch)
            elif ch == "." and not has_dot:
                digits.append(".")
                has_dot = True
        if not digits:
            return default
        try:
            return sign * float("".join(digits))
        except ValueError:
            return default


def _safe_inverse(value: float) -> float:
    if value <= 0:
        return 0.0
    return 1.0 / value


def _importance_to_score(value: Any) -> float:
    if value is None:
        return 0.0
    text = str(getattr(value, "value", value)).lower()
    mapping = {
        "low": 0.25,
        "medium": 0.5,
        "high": 0.75,
        "very_high": 1.0,
    }
    return mapping.get(text, 0.0)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _binary_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> Dict[str, float]:
    y_true = y_true.astype(int)
    y_pred = y_pred.astype(int)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    total = max(1, int(y_true.shape[0]))

    accuracy = (tp + tn) / total
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 0.0 if precision + recall == 0 else (2.0 * precision * recall) / (precision + recall)

    auc_value: Optional[float] = None
    pos_count = int(np.sum(y_true == 1))
    neg_count = int(np.sum(y_true == 0))
    if pos_count > 0 and neg_count > 0:
        order = np.argsort(y_score)
        ranks = np.empty_like(order, dtype=float)
        ranks[order] = np.arange(1, len(y_score) + 1, dtype=float)
        unique_scores, inverse, counts = np.unique(y_score, return_inverse=True, return_counts=True)
        if unique_scores.size < len(y_score):
            for i, count in enumerate(counts):
                if count > 1:
                    tie_idx = np.where(inverse == i)[0]
                    ranks[tie_idx] = float(np.mean(ranks[tie_idx]))
        rank_sum_pos = float(np.sum(ranks[y_true == 1]))
        auc_value = (rank_sum_pos - (pos_count * (pos_count + 1) / 2.0)) / float(pos_count * neg_count)
        auc_value = _clamp(float(auc_value), 0.0, 1.0)

    metrics: Dict[str, float] = {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
    }
    if auc_value is not None:
        metrics["auc"] = round(float(auc_value), 4)
    return metrics


def _build_base_signals(match: Match) -> List[float]:
    attrs = match.source_attributes if isinstance(match.source_attributes, dict) else {}
    odds_win = _to_float(attrs.get("odds_nspf_win", attrs.get("odds_win")))
    odds_draw = _to_float(attrs.get("odds_nspf_draw", attrs.get("odds_draw")))
    odds_lose = _to_float(attrs.get("odds_nspf_lose", attrs.get("odds_lose")))
    sp_win = _to_float(attrs.get("odds_spf_win"))
    sp_draw = _to_float(attrs.get("odds_spf_draw"))
    sp_lose = _to_float(attrs.get("odds_spf_lose"))
    handicap = _to_float(attrs.get("handicap", attrs.get("handicap_0")))

    odds_pair_avg = (odds_win + odds_lose) / 2.0 if (odds_win > 0 and odds_lose > 0) else 0.0
    draw_bias_main = odds_draw - odds_pair_avg if odds_draw > 0 and odds_pair_avg > 0 else 0.0
    draw_bias_sp = sp_draw - odds_draw if sp_draw > 0 and odds_draw > 0 else 0.0
    kickoff_hour = float(match.scheduled_kickoff.hour) / 24.0 if match.scheduled_kickoff else 0.0
    available_odds_cnt = float(
        sum(1 for value in [odds_win, odds_draw, odds_lose, sp_win, sp_draw, sp_lose] if value > 0)
    )

    return [
        _safe_inverse(odds_draw),  # 隐含平局概率
        abs(odds_win - odds_lose),  # 胜负差
        draw_bias_main,  # 平赔偏离
        handicap,  # 让球
        abs(handicap),  # 让球绝对值
        sp_draw,  # 北单平赔
        abs(sp_win - sp_lose),  # 北单胜负差
        draw_bias_sp,  # 北单平赔与主赔率偏离
        kickoff_hour,  # 开赛时间
        _to_float(match.popularity),  # 热度
        _importance_to_score(match.importance),  # 重要性
        available_odds_cnt,  # 可用赔率字段个数
    ]


def _build_feature_vector(selected_feature_ids: List[int], match: Match) -> Optional[List[float]]:
    base = _build_base_signals(match)
    if not base:
        return None
    total = len(base)
    values: List[float] = []
    for feature_id in selected_feature_ids:
        primary = base[(feature_id - 1) % total]
        secondary = base[((feature_id * 5) + 3) % total]
        values.append((primary * 0.72) + (secondary * 0.28))
    if not any(abs(v) > 1e-9 for v in values):
        return None
    return values


def _build_training_dataset(
    db: Session, selected_feature_ids: List[int], max_samples: int
) -> Tuple[np.ndarray, np.ndarray]:
    rows = (
        db.query(Match)
        .filter(
            Match.status == "finished",
            Match.home_score.isnot(None),
            Match.away_score.isnot(None),
        )
        .order_by(Match.match_date.desc(), Match.id.desc())
        .limit(max_samples)
        .all()
    )

    X_rows: List[List[float]] = []
    y_rows: List[int] = []
    for row in rows:
        vector = _build_feature_vector(selected_feature_ids, row)
        if vector is None:
            continue
        X_rows.append(vector)
        y_rows.append(1 if int(row.home_score) == int(row.away_score) else 0)

    if len(X_rows) < 30:
        raise RuntimeError(f"可用训练样本不足（当前 {len(X_rows)} 条，至少需要 30 条）。")

    y_array = np.asarray(y_rows, dtype=np.int32)
    pos_count = int(np.sum(y_array == 1))
    neg_count = int(np.sum(y_array == 0))
    if pos_count == 0 or neg_count == 0:
        raise RuntimeError("训练样本仅包含单一类别，无法完成二分类训练。")

    X_array = np.asarray(X_rows, dtype=np.float32)
    return X_array, y_array


def _train_numpy_logistic(
    X_train: np.ndarray, y_train: np.ndarray, epochs: int, learning_rate: float
) -> Dict[str, Any]:
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std < 1e-6] = 1.0
    Xn = (X_train - mean) / std
    y = y_train.astype(np.float32)

    weights = np.zeros(Xn.shape[1], dtype=np.float32)
    bias = 0.0
    n = float(max(1, Xn.shape[0]))

    for _ in range(max(50, epochs)):
        logits = np.clip(np.dot(Xn, weights) + bias, -20.0, 20.0)
        probs = 1.0 / (1.0 + np.exp(-logits))
        error = probs - y
        grad_w = np.dot(Xn.T, error) / n
        grad_b = float(np.mean(error))
        weights -= learning_rate * grad_w
        bias -= learning_rate * grad_b

    return {
        "type": "numpy_logistic",
        "weights": weights,
        "bias": bias,
        "mean": mean,
        "std": std,
    }


def _predict_numpy_logistic(model: Dict[str, Any], X: np.ndarray) -> np.ndarray:
    mean = model["mean"]
    std = model["std"]
    weights = model["weights"]
    bias = model["bias"]
    Xn = (X - mean) / std
    logits = np.clip(np.dot(Xn, weights) + bias, -20.0, 20.0)
    return 1.0 / (1.0 + np.exp(-logits))


def _fit_model(
    algorithm: str,
    hyperparameters: Dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    log: Callable[[str], None],
) -> Tuple[Any, Optional[Any], str]:
    algo = str(algorithm or "xgboost").strip().lower()

    if not SKLEARN_AVAILABLE:
        log("scikit-learn 不可用，回退到 numpy 逻辑回归训练。")
        epochs = int(_to_float(hyperparameters.get("epochs"), default=300))
        learning_rate = float(_to_float(hyperparameters.get("learning_rate"), default=0.05))
        model = _train_numpy_logistic(X_train, y_train, epochs=epochs, learning_rate=learning_rate)
        return model, None, "numpy_logistic"

    random_state = int(_to_float(hyperparameters.get("random_state"), default=42))

    if algo == "logistic_regression":
        max_iter = int(_to_float(hyperparameters.get("max_iter", hyperparameters.get("epochs")), default=400))
        scaler = StandardScaler()
        X_train_fit = scaler.fit_transform(X_train)
        model = LogisticRegression(
            max_iter=max(100, max_iter),
            class_weight="balanced",
            random_state=random_state,
        )
        model.fit(X_train_fit, y_train)
        return model, scaler, "logistic_regression"

    if algo == "random_forest":
        n_estimators = int(_to_float(hyperparameters.get("n_estimators"), default=300))
        max_depth_raw = hyperparameters.get("max_depth")
        max_depth = None
        if max_depth_raw not in (None, "", "None"):
            max_depth = max(2, int(_to_float(max_depth_raw, default=8)))
        model = RandomForestClassifier(
            n_estimators=max(50, n_estimators),
            max_depth=max_depth,
            random_state=random_state,
            class_weight="balanced_subsample",
            n_jobs=1,
        )
        model.fit(X_train, y_train)
        return model, None, "random_forest"

    # xgboost 默认走可用性判断，不可用时降级到 GradientBoostingClassifier。
    if algo == "xgboost":
        try:
            from xgboost import XGBClassifier  # type: ignore

            model = XGBClassifier(
                n_estimators=max(50, int(_to_float(hyperparameters.get("n_estimators"), default=240))),
                max_depth=max(2, int(_to_float(hyperparameters.get("max_depth"), default=4))),
                learning_rate=float(_to_float(hyperparameters.get("learning_rate"), default=0.05)),
                subsample=float(_clamp(_to_float(hyperparameters.get("subsample"), default=0.9), 0.2, 1.0)),
                colsample_bytree=float(
                    _clamp(_to_float(hyperparameters.get("colsample_bytree"), default=0.9), 0.2, 1.0)
                ),
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=random_state,
                n_jobs=1,
            )
            model.fit(X_train, y_train)
            return model, None, "xgboost"
        except Exception:
            log("xgboost 不可用，自动降级为 GradientBoostingClassifier。")
            model = GradientBoostingClassifier(
                n_estimators=max(50, int(_to_float(hyperparameters.get("n_estimators"), default=240))),
                learning_rate=float(_to_float(hyperparameters.get("learning_rate"), default=0.05)),
                max_depth=max(2, int(_to_float(hyperparameters.get("max_depth"), default=3))),
                random_state=random_state,
            )
            model.fit(X_train, y_train)
            return model, None, "gradient_boosting_fallback"

    # 未识别算法统一回退到逻辑回归
    log(f"未知算法 {algorithm}，已回退为 logistic_regression。")
    scaler = StandardScaler()
    X_train_fit = scaler.fit_transform(X_train)
    model = LogisticRegression(max_iter=400, class_weight="balanced", random_state=random_state)
    model.fit(X_train_fit, y_train)
    return model, scaler, "logistic_regression_fallback"


def _predict_scores(model: Any, scaler: Optional[Any], X_test: np.ndarray, model_kind: str) -> np.ndarray:
    if model_kind == "numpy_logistic":
        return _predict_numpy_logistic(model, X_test)
    X_input = scaler.transform(X_test) if scaler is not None else X_test
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_input)
        if proba.ndim == 2 and proba.shape[1] >= 2:
            return proba[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X_input)
        return 1.0 / (1.0 + np.exp(-np.clip(scores, -20.0, 20.0)))
    preds = model.predict(X_input)
    return np.asarray(preds, dtype=np.float32)


def train_job_with_real_data(
    db: Session,
    job_id: int,
    *,
    log_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    def log(message: str) -> None:
        if log_callback:
            log_callback(message)

    job = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()
    if not job:
        raise RuntimeError(f"训练任务不存在: {job_id}")

    feature_ids = job.feature_set_ids if isinstance(job.feature_set_ids, list) else []
    selected_feature_ids = []
    for item in feature_ids:
        try:
            v = int(item)
        except (TypeError, ValueError):
            continue
        if v > 0:
            selected_feature_ids.append(v)
    if not selected_feature_ids:
        raise RuntimeError("训练任务缺少 feature_set_ids，无法执行真实训练。")

    feature_rows = (
        db.query(DrawFeature)
        .filter(DrawFeature.id.in_(selected_feature_ids), DrawFeature.is_active.is_(True))
        .order_by(DrawFeature.id.asc())
        .all()
    )
    if len(feature_rows) != len(set(selected_feature_ids)):
        existing_ids = {int(row.id) for row in feature_rows}
        missing_or_inactive = sorted(set(selected_feature_ids) - existing_ids)
        raise RuntimeError(f"训练特征不存在或已禁用: {missing_or_inactive}")

    hyperparameters = job.hyperparameters if isinstance(job.hyperparameters, dict) else {}
    max_samples = int(_to_float(hyperparameters.get("max_samples"), default=4000))
    max_samples = max(200, min(20000, max_samples))

    log("准备训练数据集（来源: matches 表真实完赛数据）...")
    X, y = _build_training_dataset(db, selected_feature_ids, max_samples=max_samples)
    sample_count = int(X.shape[0])
    draw_count = int(np.sum(y == 1))
    non_draw_count = int(np.sum(y == 0))
    log(f"样本构建完成: total={sample_count}, draw={draw_count}, non_draw={non_draw_count}")

    validation_split = float(_to_float(hyperparameters.get("validation_split"), default=0.2))
    validation_split = float(_clamp(validation_split, 0.1, 0.4))
    random_state = int(_to_float(hyperparameters.get("random_state"), default=42))

    if SKLEARN_AVAILABLE:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=validation_split,
            random_state=random_state,
            stratify=y,
        )
    else:
        n = X.shape[0]
        split = int(n * (1.0 - validation_split))
        split = max(1, min(n - 1, split))
        perm = np.random.RandomState(random_state).permutation(n)
        train_idx = perm[:split]
        test_idx = perm[split:]
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

    log(
        "开始真实训练: "
        f"algorithm={job.algorithm}, train={int(X_train.shape[0])}, test={int(X_test.shape[0])}, "
        f"features={len(selected_feature_ids)}"
    )
    model, scaler, model_kind = _fit_model(job.algorithm, hyperparameters, X_train, y_train, log)
    y_score = _predict_scores(model, scaler, X_test, model_kind)
    threshold = float(_to_float(hyperparameters.get("threshold"), default=0.5))
    threshold = float(_clamp(threshold, 0.05, 0.95))
    y_pred = (y_score >= threshold).astype(np.int32)
    metrics = _binary_metrics(y_test, y_pred, y_score)

    metrics["sample_count"] = sample_count
    metrics["train_samples"] = int(X_train.shape[0])
    metrics["test_samples"] = int(X_test.shape[0])
    metrics["draw_rate"] = round(float(draw_count / max(1, sample_count)), 4)
    metrics["algorithm_used"] = model_kind

    project_root = Path(__file__).resolve().parents[2]
    artifact_dir = project_root / "models" / "draw_prediction" / f"job_{job_id}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / "model.pkl"

    artifact_payload = {
        "requested_algorithm": str(job.algorithm or "xgboost"),
        "algorithm_used": model_kind,
        "selected_feature_ids": selected_feature_ids,
        "selected_feature_names": [str(row.name) for row in feature_rows],
        "hyperparameters": hyperparameters,
        "trained_at": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "model": model,
        "scaler": scaler,
    }
    with model_path.open("wb") as f:
        pickle.dump(artifact_payload, f)

    log(f"模型训练完成，已保存到: {model_path}")
    log(
        "评估结果: "
        f"accuracy={metrics.get('accuracy')}, precision={metrics.get('precision')}, "
        f"recall={metrics.get('recall')}, f1={metrics.get('f1_score')}, auc={metrics.get('auc', '-')}"
    )

    return {
        "metrics": metrics,
        "model_path": str(model_path),
    }
