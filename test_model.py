# Basic libraries
import os
import io
import sys
import math
import time
import random
import requests
import collections
import numpy as np
from os import walk
from joblib import dump, load
from tokenizers import ByteLevelBPETokenizer
from langdetect import detect

"""
How to run:
python test_model.py --tokenizer_folder tokenizer --threshold 0.5 --model_dir saved_models --website_to_test *url*
"""

# Parsing arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tokenizer_folder", type=str, default = "tokenizer", help="Folder where tokenizer files have been placed")
parser.add_argument("--threshold", type=float, default = 0.5, help="Which threshold to use for testing")
parser.add_argument("--model_dir", type=str, default = "saved_models", help="Directory of trained models.")
parser.add_argument("--website_to_test", type=str, default = "https://www.google.com", help="Website to test")

args = parser.parse_args()
tokenizerFolder = args.tokenizer_folder
savedModelDirectory = args.model_dir
websiteToTest = args.website_to_test
threshold = args.threshold

# Loading files
# Load tokenization files
tokenizer = ByteLevelBPETokenizer(
    tokenizerFolder + "/tokenizer.tok-vocab.json",
    tokenizerFolder + "/tokenizer.tok-merges.txt",
)
tokenizerVocabSize = tokenizer.get_vocab_size()
print("Tokenizer files have been loaded and the vocab size is %d..." % tokenizerVocabSize)

# Load saved model
model = load(savedModelDirectory + "/phishytics-model.joblib")
print("Model loaded...")

# Load document frequency dictionary
docDict = np.load(savedModelDirectory + "/phishytics-model-tfidf-dictionary.npy", allow_pickle=True).item()
print("Document frequency dictionary loaded...")

# Testing
print("Loading webpage...")
try:
	request = requests.get(websiteToTest)
	webpageHtml = str(request.text)
	webpageHtml = webpageHtml.replace("\n", " ")
except Exception as e:
	print('\n',e)
	print("\nAn error occurred, exiting now... ")
	exit()

# Convert text into feature vector
output = tokenizer.encode(webpageHtml)
outputDict = collections.Counter(output.ids)

# Apply tfidf weighting
totalFilesUnderConsideration = docDict["totalFilesUnderConsideration"]
array = [0] * tokenizerVocabSize
for item in outputDict:
	if len(docDict[item]) > 0:
		array[item] = (outputDict[item]) * (math.log10( totalFilesUnderConsideration / len(docDict[item])))

# Getting predictions
predictionProbability = model.predict_proba([array])[0][1]
print("\n****************************\n--> Probability that the website is phishing: %.2f" % (predictionProbability))

prediction = "NOT PHISHING"
if predictionProbability > threshold:
	prediction = "PHISHING"
print("--> Based on your threshold of 0.50, this website is +++'%s'+++" % (prediction))
print("****************************")





# Import necessary libraries
import matplotlib.pyplot as plt

# Define your actual data for thresholds, accuracies, and losses
thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
accuracies = [0.85, 0.88, 0.90, 0.92, 0.94]  # Replace with your accuracy values
losses = [0.35, 0.30, 0.25, 0.20, 0.18]  # Replace with your loss values

# Create the accuracy graph
plt.figure(figsize=(8, 6))
plt.plot(thresholds, accuracies, marker='o', linestyle='-')
plt.title('Accuracy vs. Threshold')
plt.xlabel('Threshold')
plt.ylabel('Accuracy')
plt.grid(True)
plt.show()

# Create the loss graph
plt.figure(figsize=(8, 6))
plt.plot(thresholds, losses, marker='o', linestyle='-')
plt.title('Loss vs. Threshold')
plt.xlabel('Threshold')
plt.ylabel('Loss')
plt.grid(True)
plt.show()
