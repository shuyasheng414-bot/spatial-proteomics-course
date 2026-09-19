"""Reproducible LOPIT classification; only pd.markers supplies target labels."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.decomposition import PCA
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay, f1_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

SEED = 42
FEATURES = [f"area {i}" for i in range(114, 118)]
ROOT = Path(__file__).resolve().parents[1]


def load_data(root=ROOT):
    """Verify identifiers and intensities before row-wise normalisation."""
    raw = pd.read_csv(root / "data" / "tan2009_rep1.csv")
    assert raw["FBgn"].is_unique, "Duplicate protein identifiers"
    x = raw[FEATURES].apply(pd.to_numeric, errors="raise")
    assert np.isfinite(x.to_numpy()).all(), "Missing/non-finite intensity"
    assert (x >= 0).all().all() and (x.sum(axis=1) > 0).all()
    labels = raw["pd.markers"].fillna("unknown").astype(str).str.strip()
    raw["label"] = labels
    x = x.div(x.sum(axis=1), axis=0)
    assert np.allclose(x.sum(axis=1), 1)
    return raw, x


def prepare_split(raw, x):
    """Keep classes with >=6 markers; quarantine rare labelled classes."""
    counts = raw.loc[raw.label != "unknown", "label"].value_counts()
    eligible = counts[counts >= 6].index.tolist()
    known = raw.label.isin(eligible)
    train, test = train_test_split(
        raw.index[known].to_numpy(), test_size=0.30,
        random_state=SEED, stratify=raw.loc[known, "label"],
    )
    assert set(train).isdisjoint(test)
    assert set(raw.loc[train, "label"]) == set(raw.loc[test, "label"])
    return counts, eligible, known, train, test


def compare_models(raw, x, train):
    """Select using training folds only. Never use held-out test metrics."""
    models = {
        "Dummy": DummyClassifier(strategy="most_frequent"),
        "SVM": make_pipeline(StandardScaler(), SVC(
            C=1.0, kernel="rbf", gamma="scale", class_weight="balanced")),
        "RandomForest": RandomForestClassifier(
            n_estimators=300, class_weight="balanced", random_state=SEED,
            n_jobs=1),
    }
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED)
    y = raw.loc[train, "label"]
    assert y.value_counts().min() >= 3
    rows = []
    for name, model in models.items():
        scores = cross_validate(
            model, x.loc[train], y, cv=cv,
            scoring={"macro_f1": "f1_macro", "accuracy": "accuracy"},
            error_score="raise", n_jobs=1,
        )
        rows.append({
            "model": name,
            "cv_macro_f1_mean": scores["test_macro_f1"].mean(),
            "cv_macro_f1_sd": scores["test_macro_f1"].std(ddof=1),
            "cv_accuracy_mean": scores["test_accuracy"].mean(),
        })
    comparison = pd.DataFrame(rows).set_index("model")
    # The dummy is a reference, not a candidate biological model.
    winner = comparison.loc[["SVM", "RandomForest"], "cv_macro_f1_mean"].idxmax()
    fitted = clone(models[winner]).fit(x.loc[train], y)
    return comparison, winner, fitted, models[winner]


def evaluate(raw, x, test, fitted, classes):
    truth = raw.loc[test, "label"]
    pred = fitted.predict(x.loc[test])
    metrics = {
        "accuracy": float(accuracy_score(truth, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(truth, pred)),
        "macro_f1": float(f1_score(truth, pred, average="macro")),
    }
    report = pd.DataFrame(classification_report(
        truth, pred, labels=classes, output_dict=True, zero_division=0)).T
    return metrics, report, truth, pred


def make_figures(raw, x, counts, eligible, known, train, test, truth, pred, out):
    plt.rcParams.update({"font.size": 10, "figure.dpi": 130})
    colors = dict(zip(eligible, plt.get_cmap("tab10").colors))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    counts.sort_values().plot.barh(ax=ax, color="#307e9c")
    ax.axvline(6, color="#b9473f", linestyle="--", label="Eligibility threshold: 6")
    ax.set(xlabel="Number of reference markers", title="Reference-label imbalance")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out / "marker_counts.png")
    plt.close(fig)

    # PCA and its scaling fit only on training markers.
    scaler = StandardScaler().fit(x.loc[train])
    pca = PCA(n_components=2).fit(scaler.transform(x.loc[train]))
    z = pca.transform(scaler.transform(x))
    fig, ax = plt.subplots(figsize=(9, 5.8))
    unknown = raw.label == "unknown"
    ax.scatter(z[unknown, 0], z[unknown, 1], c="#d1d5db", s=12,
               alpha=0.4, label="Unlabelled")
    for label in eligible:
        mask = raw.label == label
        ax.scatter(z[mask, 0], z[mask, 1], s=29, label=label, color=colors[label])
    ax.set(xlabel=f"PC1 ({pca.explained_variance_ratio_[0]:.1%})",
           ylabel=f"PC2 ({pca.explained_variance_ratio_[1]:.1%})",
           title="LOPIT profiles: PCA fitted on training markers")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "pca.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 7.5))
    cm = confusion_matrix(truth, pred, labels=eligible)
    ConfusionMatrixDisplay(cm, display_labels=eligible).plot(
        ax=ax, cmap="Blues", colorbar=False, xticks_rotation=65)
    ax.set_title("Held-out test set: counts, not training performance")
    fig.tight_layout()
    fig.savefig(out / "confusion_matrix.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    for label in eligible:
        means = x.loc[raw.label == label].mean()
        ax.plot(range(4), means, marker="o", color=colors[label], label=label)
    ax.set(xticks=range(4), xticklabels=["114", "115", "116", "117"],
           xlabel="iTRAQ channel (fraction pool)", ylabel="Mean relative intensity",
           title="Reference-marker profiles (descriptive, all markers)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "profiles.png")
    plt.close(fig)
    return pca.explained_variance_ratio_.tolist()


def run_analysis(root=ROOT):
    out = root / "results"
    out.mkdir(exist_ok=True)
    raw, x = load_data(root)
    counts, classes, known, train, test = prepare_split(raw, x)
    comparison, winner, fitted, template = compare_models(raw, x, train)
    metrics, report, truth, pred = evaluate(raw, x, test, fitted, classes)
    comparison.to_csv(out / "cross_validation.csv")
    report.to_csv(out / "classification_report.csv")
    split = raw[["FBgn", "label"]].copy()
    split["split"] = "unlabelled"
    split.loc[(raw.label != "unknown") & ~known, "split"] = "rare_class_excluded"
    split.loc[train, "split"] = "train"
    split.loc[test, "split"] = "test"
    split.to_csv(out / "split.csv", index=False)
    heldout = raw.loc[test, ["FBgn", "Flybase Symbol", "label"]].copy()
    heldout["prediction"] = pred
    heldout.to_csv(out / "test_predictions.csv", index=False)
    variance = make_figures(raw, x, counts, classes, known, train, test, truth, pred, out)

    # Refit only after the independent evaluation is complete.
    final_model = clone(template).fit(x.loc[known], raw.loc[known, "label"])
    unknown = raw.label == "unknown"
    candidates = raw.loc[unknown, ["FBgn", "Flybase Symbol"]].copy()
    candidates["predicted_compartment"] = final_model.predict(x.loc[unknown])
    candidates["interpretation"] = "candidate_only_not_experimentally_validated"
    candidates.to_csv(out / "unlabelled_predictions.csv", index=False)
    summary = {
        "random_seed": SEED, "proteins": len(raw), "features": len(FEATURES),
        "reference_markers": int((raw.label != "unknown").sum()),
        "eligible_markers": int(known.sum()), "classes": classes,
        "excluded_rare_classes": counts[counts < 6].to_dict(),
        "train_n": len(train), "test_n": len(test),
        "unknown_n": int(unknown.sum()), "selected_model": winner,
        "test_metrics": metrics, "pca_variance_ratio": variance,
    }
    (out / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary, comparison, report, candidates


if __name__ == "__main__":
    summary, *_ = run_analysis()
    print(json.dumps(summary, indent=2))
