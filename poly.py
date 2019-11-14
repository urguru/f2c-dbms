from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import train_test_split

df = pd.read_csv('data.csv')
X = df[['Rainfall', 'Exchange', 'Season']]
Y = df['Cost']
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3)

regressor = LinearRegression()
poly_reg = PolynomialFeatures(degree=7)

x_poly = poly_reg.fit_transform(X)
regressor.fit(x_poly, Y)

y_pred = regressor.predict(poly_reg.fit_transform(X_test))

print('Polynomial Linear Regression Accuracy:',regressor.score(poly_reg.fit_transform(X_test), y_test))
