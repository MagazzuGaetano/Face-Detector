import time
import numpy as np
from numpy import savetxt
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, GridSearchCV

from utils import calculate_features
from utils import load_images_from_folder

import joblib

target_size = (64, 64)

# Load images
LWZ_data_path = 'data-path'
Caltech_256_data_path = 'data-path'
Natural_images_data_path ='data-path'
Dtd_texture_data_path ='data-path'

N = 1000 #int(13000 / 8) #number of images to keep from the LWZ Dataset
M = 4000 #int(26000 / 8) #number of images to keep from the Caltech_256 Dataset
L = int(4000 / 4) #number of images to keep from the Natural_images Dataset
K = int(2000 / 4) #number of images to keep from the Dtd_texture Dataset

faces = np.asarray(load_images_from_folder(LWZ_data_path + '/faces', target_size[1], target_size[0], N))[:N]
not_faces = np.asarray(load_images_from_folder(Caltech_256_data_path, target_size[1], target_size[0], M))[:M]
#not_faces2 = np.asarray(load_images_from_folder(Natural_images_data_path, target_size[1], target_size[0]))[:L]
#not_faces3 = np.asarray(load_images_from_folder(Dtd_texture_data_path, target_size[1], target_size[0]))[:K]


print(faces.shape)
print(not_faces.shape)
#print(not_faces2.shape)
#print(not_faces3.shape)

images = np.concatenate([faces, not_faces]) #not_faces2, not_faces3])

# Label images (N faces and M non-faces)
y = np.array([1] * N + [0] * M)

print("Data Loaded into Memory!")


# calculate features
X = calculate_features(images)

print(X.shape)

std_scaler = None
pca_scaler = None


std_scaler = StandardScaler()
std_scaler.fit(X)
X = std_scaler.transform(X)
print(X.shape)

pca_scaler = PCA(0.95)
pca_scaler.fit(X)
X = pca_scaler.transform(X)


X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.2, random_state=42, stratify=y
)


savetxt("X_train.csv", X_train)
savetxt("y_train.csv", y_train)
savetxt("X_test.csv", X_test)
savetxt("y_test.csv", y_test)


clf = LinearSVC(class_weight=None, dual=True, fit_intercept=True,
                intercept_scaling=1, loss='squared_hinge',
                multi_class='ovr', penalty='l2', max_iter=1000, tol=1e-4, 
                random_state=0, verbose=0)
clf = SVC(kernel="linear", probability=True)
grid = GridSearchCV(clf, {'C': [0.01, 0.1, 1, 10]}, n_jobs=-1, cv=10)
grid.fit(X_train, y_train)
print('best_score: {}, best_params: {}'.format(grid.best_score_, grid.best_params_))

clf = model = grid.best_estimator_
t_start = time.time()
clf.fit(X_train, y_train)
time_train = time.time() - t_start
print("time_{}_train: --- {} seconds ---".format("model", time_train))

joblib.dump([std_scaler, pca_scaler, clf], 'model.sav', compress=1)
