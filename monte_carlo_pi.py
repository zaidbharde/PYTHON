import random

def estimate_pi(num_samples):
    inside_circle = 0
    for _ in range(num_samples):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        if x*x + y*y <= 1:
            inside_circle += 1
    return 4 * inside_circle / num_samples


if __name__ == "__main__":
    for n in [1000, 10000, 100000, 1000000]:
        pi_est = estimate_pi(n)
        print(f"Samples: {n:>8} -> Pi estimate: {pi_est:.5f}")
