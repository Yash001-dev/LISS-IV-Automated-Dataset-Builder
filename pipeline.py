import subprocess

steps = [

    "find_overlaps.py",

    "create_training_pairs.py",

    "align_all_pairs.py",

    "extract_patches.py"

]

for step in steps:

    print()
    print("=" * 50)

    print(
        f"Running {step}"
    )

    print("=" * 50)

    result = subprocess.run(

        [
            "python",
            step
        ]

    )

    if result.returncode != 0:

        print(
            f"ERROR in {step}"
        )

        break

print()
print(
    "Pipeline Finished"
)