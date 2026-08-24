"""Small manual smoke test kept for editor compatibility.

The production implementation lives in :mod:`zero_shot_category`; keeping a
second copy here previously allowed the two classifiers to diverge.
"""

from .zero_shot_category import classify_category

if __name__ == "__main__":
    samples = [
        "وی پی ان من وصل نمی‌شود و احراز هویت خطا می‌دهد",
        "حجم ایمیل من پر شده است",
        "وای فای طبقه دوم قطع شده است",
        "پرینتر کاغذ گیر کرده و چاپ انجام نمی‌شود",
        "رمز سامانه را فراموش کرده‌ام",
    ]

    for sample in samples:
        print(classify_category(sample, debug=True))
