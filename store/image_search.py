import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model
from sklearn.neighbors import NearestNeighbors
from .models import Product


base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
model = Model(inputs=base_model.input, outputs=base_model.output)

def extract_image_features(img):
    img = keras_image.load_img(img, target_size=(224, 224))
    img_data = keras_image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    features = model.predict(img_data)
    return features.flatten()


def find_similar_products(features, n_neighbors=5):
    product_features = []
    product_ids = []

    for product in Product.objects.exclude(image=''):
        img_path = product.image.url
        product_features.append(extract_image_features(img_path))
        product_ids.append(product.id)
    
    neighbors = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(product_features)
    distances, indices = neighbors.kneighbors([features])
    
    similar_products = [Product.objects.get(id=product_ids[idx]) for idx in indices[0]]
    return similar_products
