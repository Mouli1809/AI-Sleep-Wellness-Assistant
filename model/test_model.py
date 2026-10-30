
import os
import sys
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MODEL_PATH = os.path.join("model", "sleep_model.pkl")
META_PATH = os.path.join("model", "model_metadata.json")
DATA_PATH = os.path.join("data", "sleep_dataset.csv")

FEATURE_COLUMNS = [
    "sleep_duration", "bedtime_hour", "wake_hour", "previous_sleep_duration",
    "stress_level", "physical_activity", "hydration", "screen_time",
    "noise_level", "temperature_comfort", "light_level", "bed_comfort"
]

BASELINE = dict(
    sleep_duration=8.0, bedtime_hour=22.5, wake_hour=6.5, previous_sleep_duration=8.0,
    stress_level=3, physical_activity=60, hydration=3.0, screen_time=20,
    noise_level=2, temperature_comfort=9, light_level=2, bed_comfort=9,
)

failures = []


def check(condition, message):
    print(("[PASS] " if condition else "[FAIL] ") + message)
    if not condition:
        failures.append(message)


def frame(**overrides):
    row = {**BASELINE, **overrides}
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


def run_model_tests():
    print("=" * 60)
    print("[TEST] SLEEP MODEL TEST SUITE")
    print("=" * 60)

    print("\n--- Test 1: Artifacts exist and load ---")
    for p in (MODEL_PATH, META_PATH, DATA_PATH):
        check(os.path.exists(p), f"{p} exists")
    pipeline = joblib.load(MODEL_PATH)
    with open(META_PATH) as f:
        meta = json.load(f)
    print(f"  Model: {meta.get('model_name')} | trained {meta.get('trained_at')}")

    print("\n--- Test 2: Held-out accuracy (the only valid accuracy number) ---")
    df = pd.read_csv(DATA_PATH)
    X, y = df[FEATURE_COLUMNS], df["sleep_quality"]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"  Held-out accuracy on {len(y_test)} unseen rows: {acc*100:.2f}%")
    recorded = meta.get("accuracy")
    check(abs(acc - recorded) < 0.01, f"matches accuracy recorded in metadata ({recorded*100:.2f}%)")
    check(acc >= 0.75, "held-out accuracy >= 75%")
    labels = list(pipeline.classes_)
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print("\n  Confusion matrix (rows = true, cols = predicted):")
    print(pd.DataFrame(cm, index=[f"True {l}" for l in labels], columns=[f"Pred {l}" for l in labels]))
    print("\n" + classification_report(y_test, y_pred))

    print("--- Test 3: Scenario predictions (must be correct) ---")
    scenarios = [
        ("Optimal health -> Good", "Good", {}),
        ("High stress, long screen, 4.5h sleep -> Poor", "Poor", dict(
            sleep_duration=4.5, bedtime_hour=1.5, wake_hour=6.0, previous_sleep_duration=5.0,
            stress_level=9, physical_activity=0, hydration=1.0, screen_time=150,
            noise_level=8, temperature_comfort=3, light_level=8, bed_comfort=4)),
        ("Moderate lifestyle -> Average", "Average", dict(
            sleep_duration=6.5, bedtime_hour=23.5, wake_hour=6.0, previous_sleep_duration=6.0,
            stress_level=6, physical_activity=30, hydration=2.0, screen_time=60,
            noise_level=5, temperature_comfort=6, light_level=5, bed_comfort=6)),
    ]
    for name, expected, overrides in scenarios:
        pred = pipeline.predict(frame(**overrides))[0]
        check(pred == expected, f"{name} (got {pred})")

    print("\n--- Test 4: Behavioural sanity ---")
    # Use a mid-range profile so probabilities are NOT saturated at 0 or 1; otherwise
    # "more stress lowers P(Good)" would pass trivially (e.g. 1.00 -> 0.99).
    mid = dict(sleep_duration=6.5, bedtime_hour=23.5, wake_hour=6.0, previous_sleep_duration=6.0,
               stress_level=5, physical_activity=30, hydration=2.0, screen_time=60,
               noise_level=5, temperature_comfort=6, light_level=5, bed_comfort=6)
    classes = list(pipeline.classes_)
    gi = classes.index("Good")

    def p_good(**o):
        return pipeline.predict_proba(frame(**{**mid, **o}))[0][gi]

    p_low, p_high = p_good(stress_level=2), p_good(stress_level=9)
    check(p_low - p_high > 0.30, f"stress 2 -> 9 lowers P(Good) by >0.30 ({p_low:.2f} -> {p_high:.2f})")
    p_lo, p_hi = p_good(screen_time=10), p_good(screen_time=170)
    check(p_lo - p_hi > 0.30, f"pre-bed screen 10 -> 170 min lowers P(Good) by >0.30 ({p_lo:.2f} -> {p_hi:.2f})")
    p_8, p_5 = p_good(sleep_duration=8.0, stress_level=3), p_good(sleep_duration=5.0, stress_level=3)
    check(p_8 > p_5, f"8h sleep is rated better than 5h at equal stress ({p_8:.2f} vs {p_5:.2f})")
    for dur in (2.0, 14.0):  # the UI allows these, training data only covers 4-10h
        pred = pipeline.predict(frame(sleep_duration=dur))[0]
        check(pred != "Good", f"out-of-range {dur}h sleep is not rated 'Good' (got {pred})")

    print("\n" + "=" * 60)
    if failures:
        print(f"[FAILED] {len(failures)} check(s) failed:")
        for m in failures:
            print("  -", m)
        sys.exit(1)
    print("[SUCCESS] ALL CHECKS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_model_tests()