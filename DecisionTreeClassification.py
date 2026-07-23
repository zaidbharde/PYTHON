import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, ConfusionMatrixDisplay


def load_data() -> tuple:
    """
    Load the Iris dataset and return features, labels, and metadata.

    Returns
    -------
    X            : feature matrix  (n_samples, n_features)
    y            : label vector    (n_samples,)
    feature_names: list of feature name strings
    class_names  : list of class name strings
    """
    dataset = load_iris()
    return dataset.data, dataset.target, dataset.feature_names, dataset.target_names


def build_model(max_depth: int = 4, random_state: int = 42) -> DecisionTreeClassifier:
    """
    Create a Decision Tree classifier.

    Parameters
    ----------
    max_depth    : limits tree depth to prevent overfitting and keep the
                   visualization readable
    random_state : seed for reproducibility
    """
    return DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)


def evaluate(
    model: DecisionTreeClassifier,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
) -> None:
    """Print a classification report and display a confusion matrix."""
    y_pred = model.predict(X_test)

    print("=" * 52)
    print("Classification Report")
    print("=" * 52)
    print(classification_report(y_test, y_pred, target_names=class_names))

    # Confusion matrix
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_test,
        y_pred,
        display_labels=class_names,
        colorbar=False,
        ax=ax,
    )
    ax.set_title("Confusion Matrix — Iris Decision Tree")
    plt.tight_layout()
    plt.show()


def visualize_tree(
    model: DecisionTreeClassifier,
    feature_names: list[str],
    class_names: list[str],
) -> None:
    """Render the decision tree structure."""
    fig, ax = plt.subplots(figsize=(18, 8))
    plot_tree(
        model,
        filled=True,
        rounded=True,                    # rounded boxes look cleaner
        feature_names=feature_names,
        class_names=class_names,         # show class names instead of raw IDs
        impurity=True,                   # show Gini impurity per node
        proportion=False,                # show raw sample counts
        ax=ax,
    )
    ax.set_title(
        f"Decision Tree (max_depth={model.max_depth})",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.show()


def predict_samples(
    model: DecisionTreeClassifier,
    samples: np.ndarray,
    class_names: list[str],
    feature_names: list[str],
) -> None:
    """
    Print a formatted prediction for each sample.
    
    Parameters
    ----------
    samples : 2-D array of shape (n_samples, n_features)
    """
    predictions = model.predict(samples)
    probabilities = model.predict_proba(samples)

    print("\nSample Predictions")
    print("=" * 52)

    feature_widths = [len(name) for name in feature_names]
    for sample, pred, prob in zip(samples, predictions, probabilities):
        print("\n  Features:")
        for name, value, width in zip(feature_names, sample, feature_widths):
            print(f"    {name:<{width}} : {value:.2f}")
        print(f"  Predicted class : {class_names[pred]!r}")
        print(f"  Class probabilities:")
        for name, p in zip(class_names, prob):
            bar = "█" * int(p * 20)
            print(f"    {name:<15} {p:.2%}  {bar}")


def main() -> None:
    # ── 1. Load data ──────────────────────────────────────────────────
    X, y, feature_names, class_names = load_data()

    # ── 2. Train / test split ─────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y,           # keep class balance in both splits
    )

    # ── 3. Train ──────────────────────────────────────────────────────
    model = build_model(max_depth=4)
    model.fit(X_train, y_train)

    print(f"Training samples : {len(X_train)}")
    print(f"Test samples     : {len(X_test)}")
    print(f"Tree depth       : {model.get_depth()}")
    print(f"Number of leaves : {model.get_n_leaves()}")

    # ── 4. Evaluate ───────────────────────────────────────────────────
    evaluate(model, X_test, y_test, class_names)

    # ── 5. Visualize tree ─────────────────────────────────────────────
    visualize_tree(model, feature_names, class_names)

    # ── 6. Predict specific samples ───────────────────────────────────
    samples_to_predict = np.array([
        X_test[0],                           # a real test sample
        [5.1, 3.5, 1.4, 0.2],               # classic setosa example
        [6.7, 3.0, 5.2, 2.3],               # likely virginica
    ])
    predict_samples(model, samples_to_predict, class_names, feature_names)


if __name__ == "__main__":
    main()
