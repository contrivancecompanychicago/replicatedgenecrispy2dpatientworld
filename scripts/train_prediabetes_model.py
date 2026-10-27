from pathlib import Path

from patientworld.ml_pipeline import create_synthetic_dataset


def main() -> None:
    output_dir = Path("examples")
    output_dir.mkdir(exist_ok=True)
    train_path = output_dir / "prediabetes_train.csv"
    val_path = output_dir / "prediabetes_val.csv"

    df = create_synthetic_dataset(output_dir / "prediabetes_full.csv", n_samples=2500, seed=42)
    train_df = df.sample(frac=0.8, random_state=42)
    val_df = df.drop(train_df.index)
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    print(f"Generated training data: {train_path}")
    print(f"Generated validation data: {val_path}")


if __name__ == "__main__":
    main()
