import pandas as pd
import joblib

from preprocessing import clean_text

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_excel("archive/dataset/phishing_dataset.xlsx")

# Combine subject and email text
df["text"] = df["subject"] + " " + df["email_text"]

# Clean text
df["text"] = df["text"].apply(clean_text)

# Features and labels
X = df["text"]
y = df["label"]

# Convert text into TF-IDF features
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(X)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Models to compare
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Naive Bayes": MultinomialNB(),
    "Random Forest": RandomForestClassifier(random_state=42),
    "Support Vector Machine": LinearSVC()
}

best_model = None
best_accuracy = 0
best_name = ""

print("=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

for name, model in models.items():

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"{name:<25} : {accuracy * 100:.2f}%")

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model
        best_name = name

# Save best model
joblib.dump(best_model, "archive/models/phishing_model.pkl")
joblib.dump(vectorizer, "archive/models/vectorizer.pkl")

print("\n" + "=" * 60)
print(f"Best Model : {best_name}")
print(f"Accuracy   : {best_accuracy * 100:.2f}%")
print("=" * 60)

print("\nBest model saved successfully!")