import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
df = pd.read_csv('data.csv')
reg = linear_model.LinearRegression()

X=df[['Rainfall','Exchange','Season']]
Y=df['Cost']
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3)
clf = LinearRegression()
clf.fit(X_train, y_train)
print(clf.score(X_test, y_test))

