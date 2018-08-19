
# coding: utf-8

# In[3]:


#!/bin/env/python3

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def load_data(train_path, test_path):
    """
    Load the training and testing data into Pandas DataFrame.
    Args:
        train_path: String path to training dataset.
        test_path: String path to testing dataset.
    Returns:
        train_data: Training data formatted into Pandas DataFrame.
        test_data: Testing data formatted into Pandas DataFrame.
    """
    col_names = ["age", "workclass", "fnlwgt", "education", "education-num",
                 "marital-status", "occupation", "relationship", "race",
                 "sex", "capital-gain", "capital-loss", "hours-per-week",
                 "native-country", "income"]
    train_data = pd.read_csv(train_path, header=None, names=col_names)
    test_data = pd.read_csv(test_path, header=None, names=col_names)

    print("Training Data Loaded.")
    print("Total training instances:", len(train_data))
    print("Total testing instances:", len(test_data), "\n")

    return train_data, test_data


def clean_data(train_data, test_data):
    """
    Clean the training and testing data by removing invalid data points.
    Args:
        train_data: Train data as Pandas DataFrame.
        test_data: Test data as Pandas DataFrame.
    Returns:
        train_clean: Cleaned testing data in Pandas DataFrame.
        test_clean: Cleaned testing data in Pandas DataFrame.
    """
    # Replace all " ?" with NaN and then drop rows where NaN appears
    train_clean = train_data.replace(' ?', np.nan).dropna()
    test_clean = test_data.replace(' ?', np.nan).dropna()

    print("Number or training instances removed:", len(train_data) - len(train_clean))
    print("Number or testing instances removed:", len(test_data) - len(test_clean))
    print("Total training instances:", len(train_clean))
    print("Total testing instances:", len(test_clean), "\n")

    return train_clean, test_clean


def standardize_data(train_data, test_data):
    """
    Standardize the train and test data to have 0 mean and unit variance.
    Args:
        train_data: Train data as Pandas DataFrame.
        test_data: Test data as Pandas DataFrame.
    Returns:
        train_data: Standardized train data as Pandas DataFrame.
        test_data: Standardized test data as Pandas DataFrame.
    """
    # Fit scaler on train data only. Transform training and testing set
    numerical_col = ["age", "fnlwgt", "education-num", "capital-gain",
                     "capital-loss", "hours-per-week"]
    scaler = StandardScaler()
    train_data[numerical_col] = scaler.fit_transform(train_data[numerical_col])
    test_data[numerical_col] = scaler.transform(test_data[numerical_col])

    return train_data, test_data


def split_data(train_data, test_data):
    """
    Split data into training/testing features and training/testing labels.
    Args:
        train_data: Train dataset as Pandas DataFrame.
        test_data: Test dataset as Pandas DataFrame.
    Returns:
        X_train: Train features as Pandas DataFrame.
        y_train: Train labels as Pandas Series.
        X_test: Test features as Pandas DataFrame.
        y_test: Test labels as Pandas Series.
    """
    y_train = train_data["income"]
    X_train = train_data.drop("income", axis=1)

    y_test = test_data['income']
    X_test = test_data.drop("income", axis=1)

    return X_train, y_train, X_test, y_test


def ohe_data(X_train, y_train, X_test, y_test):
    """
    One hot encode categorical data.
    Args:
        X_train: Train features as Pandas DataFrame.
        y_train: Train labels as Pandas Series.
        X_test: Test features as Pandas DataFrame.
        y_test: Test labels as Pandas Series.
    Returns:
        X_train_ohe: One-hot encoded training features as Pandas DataFrame.
        y_train_ohe: One-hot encoded training labels as Pandas Series.
        X_test_ohe: One-hot encoded testing features as Pandas DataFrame.
        y_test_ohe: One-hot encoded testing labels as Pandas Series.
    """
    data = pd.concat([X_train, X_test])
    data_ohe = pd.get_dummies(data)
    X_train_ohe = data_ohe[:len(X_train)]
    X_test_ohe = data_ohe[len(X_train):]

    y_train_ohe = y_train.replace([' <=50K', ' >50K'], [0, 1])
    y_test_ohe = y_test.replace([' <=50K', ' >50K'], [0, 1])

    return X_train_ohe, y_train_ohe, X_test_ohe, y_test_ohe






from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.grid_search import GridSearchCV
import argparse
import os
from data_preprocessing import *


def preprocess_data():
    """
    Preprocess the data.
    Args:
        None
    Returns:
        X_train: Training features as Pandas DataFrame.
        y_train: Training labels as Pandas Series.
        X_test: Testing features as Pandas DataFrame.
        y_test: Testing labels as Pandas Series.
    """
    path_to_train = "data" + os.sep + "train_data.txt"
    path_to_test = "data" + os.sep + "test_data.txt"

    # Load the data
    print("Loading data...")
    train_data, test_data = load_data(path_to_train, path_to_test)
    # Clean the data
    print("Cleaning data...")
    train_clean, test_clean = clean_data(train_data, test_data)
    # Standardize the data
    print("Standardizing the data...")
    train_data, test_data = standardize_data(train_data, test_data)
    # Split data into features and labels
    X_train, y_train, X_test, y_test = split_data(train_data, test_data)
    # One-hot encode the data
    X_train, y_train, X_test, y_test = ohe_data(X_train, y_train, X_test, y_test)

    return X_train, y_train, X_test, y_test


def train_and_validate(algorithm):
    """
    Train and validate machine learning model using algorithm and data provided.
    Args:
        algorithm: String defining ML algorithm to use (naive_bayes,
                   decision_tree, knn, or svm).
    Returns:
        Prints out classification accuracy.
    """
    X_train, y_train, X_test, y_test = preprocess_data()
    print("\nData sucessfully loaded.")
    input("Press ENTER to continue...")

    clf = None
    parameters = {}
    if algorithm == "naive_bayes":
        clf = GaussianNB()
    elif algorithm == "decision_tree":
        clf = DecisionTreeClassifier()
        parameters = {"criterion": ("gini", "entropy"),
                      "max_depth": (None, 2, 3),
                      "min_samples_split": (2, 3, 4)}
    elif algorithm == "knn":
        clf = KNeighborsClassifier()
        parameters = {"n_neighbors": (3, 5, 6, 8, 10, 15),
                      "weights": ("uniform", "distance")}
    elif algorithm == "svm":
        clf = SVC()
        parameters = {"C": (0.1, 1, 5, 10),
                      "kernel": ("rbf", "linear"),
                      "gamma": (0.1, 0.5, 1)}
    else:
        print("Error: Model not found.")
        return

    clf_gs = GridSearchCV(clf, parameters, verbose=1)
    print("Training model...")
    clf_gs.fit(X_train, y_train)
    y_pred = clf_gs.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("Model Accuracy:", acc * 100.0)


if __name__ == "__main__":
    """
    Run main program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clf", help="Define the type of classifier to use.")
    args = parser.parse_args()
    if args.clf == "naive_bayes":
        train_and_validate("naive_bayes")
    elif args.clf == "decision_tree":
        train_and_validate("decision_tree")
    elif args.clf == "knn":
        train_and_validate("knn")
    elif args.clf == "svm":
        train_and_validate("svm")
    else:
        print("No classifier provided. Using naive_bayes as default.")
        train_and_validate("naive_bayes")

