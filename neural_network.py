"""
Neural Network from scratch — no libraries.
Implements forward pass, backprop, and gradient descent.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple


class Layer:
    def __init__(self, input_size: int, output_size: int):
        # Xavier initialization
        self.weights = np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)
        self.biases  = np.zeros((1, output_size))
        self.input   = None
        self.output  = None
        # Gradients
        self.dW = np.zeros_like(self.weights)
        self.db = np.zeros_like(self.biases)

    def forward(self, X: np.ndarray) -> np.ndarray:
        self.input  = X
        self.output = X @ self.weights + self.biases
        return self.output

    def backward(self, grad: np.ndarray) -> np.ndarray:
        m          = self.input.shape[0]
        self.dW    = self.input.T @ grad / m
        self.db    = grad.mean(axis=0, keepdims=True)
        return grad @ self.weights.T


class Activation:
    @staticmethod
    def relu(x: np.ndarray)          -> np.ndarray: return np.maximum(0, x)
    @staticmethod
    def relu_grad(x: np.ndarray)     -> np.ndarray: return (x > 0).astype(float)
    @staticmethod
    def sigmoid(x: np.ndarray)       -> np.ndarray: return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    @staticmethod
    def sigmoid_grad(x: np.ndarray)  -> np.ndarray:
        s = Activation.sigmoid(x)
        return s * (1 - s)
    @staticmethod
    def softmax(x: np.ndarray)       -> np.ndarray:
        e = np.exp(x - x.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)


class NeuralNetwork:
    """
    Fully connected neural network with configurable layers.
    Loss: cross-entropy. Optimizer: SGD with momentum.
    """

    def __init__(self, layer_sizes: List[int], learning_rate: float = 0.01,
                 momentum: float = 0.9):
        self.layers        = [Layer(layer_sizes[i], layer_sizes[i+1])
                              for i in range(len(layer_sizes) - 1)]
        self.lr            = learning_rate
        self.momentum      = momentum
        self.velocities    = [{'W': np.zeros_like(l.weights),
                               'b': np.zeros_like(l.biases)}
                              for l in self.layers]
        self.loss_history: List[float] = []
        self.acc_history:  List[float] = []

    def forward(self, X: np.ndarray) -> np.ndarray:
        out = X
        for i, layer in enumerate(self.layers):
            out = layer.forward(out)
            # ReLU on all layers except last
            if i < len(self.layers) - 1:
                out = Activation.relu(out)
        return Activation.softmax(out)

    def compute_loss(self, y_pred: np.ndarray, y_true: np.ndarray) -> float:
        m    = y_true.shape[0]
        eps  = 1e-12
        loss = -np.sum(y_true * np.log(y_pred + eps)) / m
        return float(loss)

    def backward(self, X: np.ndarray, y_pred: np.ndarray, y_true: np.ndarray):
        # Gradient of cross-entropy + softmax
        grad = (y_pred - y_true)

        for i in reversed(range(len(self.layers))):
            grad = self.layers[i].backward(grad)
            if i > 0:
                grad *= Activation.relu_grad(self.layers[i-1].output)

    def update_weights(self):
        for i, layer in enumerate(self.layers):
            # SGD with momentum
            self.velocities[i]['W'] = (self.momentum * self.velocities[i]['W']
                                       - self.lr * layer.dW)
            self.velocities[i]['b'] = (self.momentum * self.velocities[i]['b']
                                       - self.lr * layer.db)
            layer.weights += self.velocities[i]['W']
            layer.biases  += self.velocities[i]['b']

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 1000,
            batch_size: int = 32, verbose: bool = True):
        m = X.shape[0]
        # One-hot encode
        n_classes = y.max() + 1
        Y         = np.eye(n_classes)[y]

        for epoch in range(epochs):
            # Mini-batch shuffle
            idx     = np.random.permutation(m)
            X_shuf  = X[idx]
            Y_shuf  = Y[idx]
            epoch_loss = 0.0

            for start in range(0, m, batch_size):
                Xb = X_shuf[start:start + batch_size]
                Yb = Y_shuf[start:start + batch_size]

                y_pred = self.forward(Xb)
                epoch_loss += self.compute_loss(y_pred, Yb)
                self.backward(Xb, y_pred, Yb)
                self.update_weights()

            # Track metrics
            y_pred_full = self.forward(X)
            loss = self.compute_loss(y_pred_full, Y)
            acc  = self.accuracy(X, y)
            self.loss_history.append(loss)
            self.acc_history.append(acc)

            if verbose and (epoch + 1) % 100 == 0:
                print(f"  Epoch {epoch+1:>4} | Loss: {loss:.4f} | Acc: {acc:.4f}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X).argmax(axis=1)

    def accuracy(self, X: np.ndarray, y: np.ndarray) -> float:
        return float((self.predict(X) == y).mean())

    def plot_history(self):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(self.loss_history, color='tomato')
        ax1.set_title('Training Loss')
        ax1.set_xlabel('Epoch')
        ax2.plot(self.acc_history, color='steelblue')
        ax2.set_title('Training Accuracy')
        ax2.set_xlabel('Epoch')
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    # Generate dataset
    X, y = make_classification(
        n_samples=1000, n_features=20, n_classes=3,
        n_informative=15, random_state=42
    )
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Build and train
    nn = NeuralNetwork(
        layer_sizes=[20, 64, 32, 3],
        learning_rate=0.01,
        momentum=0.9
    )

    print("Training Neural Network...")
    print("=" * 50)
    nn.fit(X_train, y_train, epochs=500, batch_size=32)

    print(f"\nTest Accuracy: {nn.accuracy(X_test, y_test):.4f}")
    nn.plot_history()
