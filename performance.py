import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.linear_model import LogisticRegression

from preprocessing import clean_text

# Load dataset
df = pd.read_excel("archive/dataset/phishing_dataset.xlsx")

# Combine text
df["text"] = df["subject"] + " " + df["email_text"]

# Clean
df["text"] = df["text"].apply(clean_text)

# Features
X = df["text"]
y = df["label"]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
X,
y,
test_size=0.2,
random_state=42
)

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

pred = model.predict(X_test)

cm = confusion_matrix(y_test, pred)

disp = ConfusionMatrixDisplay(cm)

disp.plot()

plt.title("Confusion Matrix")

plt.show()