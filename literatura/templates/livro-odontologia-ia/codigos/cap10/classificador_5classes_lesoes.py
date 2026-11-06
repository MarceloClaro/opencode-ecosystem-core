import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras import layers, Model
from odontoia.data.loader import load_oral_lesions
from odontoia.data.augment import DentalAugmentor
from odontoia.visualization import plot_gradcam_multiclass
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# ============================================================
# 1. CARREGAR DATASET (5 classes)
# ============================================================
(X_train, y_train), (X_val, y_val), (X_test, y_test) = \
    load_oral_lesions(
        'datasets/oral_lesions_5class/',
        img_size=(300, 300),   # EfficientNetV2 usa resolução progressiva
        test_split=0.15,
        val_split=0.15,
        stratify=True
    )

CLASS_NAMES = ['OSCC', 'Leucoplasia', 'Eritroplasia', 'Liquen_Plano', 'Normal']
NUM_CLASSES = 5

print(f"Treino: {X_train.shape[0]} imagens")
print(f"Distribuição: {np.bincount(y_train)}")

# ============================================================
# 2. PRÉ-PROCESSAMENTO
# ============================================================
# Normalização para EfficientNetV2 (espera entrada [0, 1])
X_train = X_train.astype('float32') / 255.0
X_val = X_val.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0

# One-hot encoding
y_train_oh = tf.keras.utils.to_categorical(y_train, NUM_CLASSES)
y_val_oh = tf.keras.utils.to_categorical(y_val, NUM_CLASSES)
y_test_oh = tf.keras.utils.to_categorical(y_test, NUM_CLASSES)

# Pesos para classes desbalanceadas
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight(
    'balanced', classes=np.unique(y_train), y=y_train
)
class_weight_dict = dict(enumerate(class_weights))
print(f"Pesos das classes: {class_weight_dict}")

# ============================================================
# 3. DATA AUGMENTATION (foco em variação intraoral)
# ============================================================
augmentor = DentalAugmentor(
    # Geométricas
    rotation_range=20,          # Maior que radiografia (±20°)
    horizontal_flip=True,
    vertical_flip=False,        # Orientação craniocaudal
    zoom_range=0.15,            # Variação de distância câmera-paciente
    translation_range=0.1,
    shear_range=0.1,            # ângulo de captura variável

    # Fotométricas (CRÍTICAS para fotografia intraoral)
    brightness_range=0.3,       # Flash vs. luz ambiente
    contrast_range=0.2,
    saturation_range=0.15,      # Variação de câmera
    hue_range=0.05,             # Balanço de branco

    # Ruído
    noise_std=0.03,             # Ruído de sensor smartphone

    target_size=(300, 300)
)

# ============================================================
# 4. CONSTRUIR MODELO (EfficientNetV2-M + cabeça odontológica)
# ============================================================
# Backbone pré-treinado
base_model = tf.keras.applications.EfficientNetV2M(
    weights='imagenet',
    include_top=False,
    input_shape=(300, 300, 3),
    include_preprocessing=False  # já pré-processamos
)

# Congelar backbone (Fase 1)
base_model.trainable = False

# Cabeça de classificação odontológica
inputs = tf.keras.Input(shape=(300, 300, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(512, activation='swish')(x)  # swish > ReLU para EfficientNet
x = layers.Dropout(0.3)(x)
x = layers.Dense(256, activation='swish')(x)
outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs, outputs)

# ============================================================
# 5. FASE 1: TREINAR CABEÇA
# ============================================================
model.compile(
    optimizer=tf.keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy',
             tf.keras.metrics.AUC(multi_label=False, name='auc_ovr')]
)

history1 = model.fit(
    augmentor.flow(X_train, y_train_oh, batch_size=32, seed=42),
    validation_data=(X_val, y_val_oh),
    epochs=20,
    class_weight=class_weight_dict,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(
            monitor='val_auc_ovr', mode='max',
            patience=5, restore_best_weights=True
        )
    ]
)

# ============================================================
# 6. FASE 2: FINE-TUNING
# ============================================================
# Descongelar últimos 40% do backbone
base_model.trainable = True
for layer in base_model.layers[:-int(len(base_model.layers)*0.4)]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.AdamW(learning_rate=1e-5, weight_decay=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy',
             tf.keras.metrics.AUC(multi_label=False, name='auc_ovr')]
)

history2 = model.fit(
    augmentor.flow(X_train, y_train_oh, batch_size=16, seed=42),  # batch menor
    validation_data=(X_val, y_val_oh),
    epochs=30,
    class_weight=class_weight_dict,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(
            monitor='val_auc_ovr', mode='max',
            patience=10, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7
        )
    ]
)

# ============================================================
# 7. AVALIAÇÃO COMPLETA
# ============================================================
y_pred_proba = model.predict(X_test)
y_pred = np.argmax(y_pred_proba, axis=1)

# Relatório de classificação
print("\n" + "="*60)
print("RELATÓRIO DE CLASSIFICAÇÃO — 5 CLASSES DE LESÕES BUCAIS")
print("="*60)
print(classification_report(y_test, y_pred, target_names=CLASS_NAMES, digits=3))

# Matriz de confusão
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
            cbar_kws={'label': 'Contagem'})
plt.title('Matriz de Confusão — Classificador de Lesões Bucais (EfficientNetV2-M)')
plt.xlabel('Predito')
plt.ylabel('Real')
plt.tight_layout()
plt.savefig('confusao_5classes_lesoes.png', dpi=150)

# Grad-CAM para interpretabilidade
sample_indices = [
    np.where(y_test == i)[0][0] for i in range(NUM_CLASSES)
]
plot_gradcam_multiclass(
    model, X_test[sample_indices],
    class_names=CLASS_NAMES,
    layer_name='block6g_activate',  # última camada conv EfficientNetV2-M
    save_path='gradcam_lesoes_bucais.png'
)

# Curvas ROC por classe (One-vs-Rest)
from sklearn.metrics import roc_curve, auc
plt.figure(figsize=(10, 8))
for i in range(NUM_CLASSES):
    fpr, tpr, _ = roc_curve(y_test_oh[:, i], y_pred_proba[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, lw=2, label=f'{CLASS_NAMES[i]} (AUC={roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', lw=1, label='Aleatório')
plt.xlabel('Taxa de Falsos Positivos')
plt.ylabel('Taxa de Verdadeiros Positivos')
plt.title('Curvas ROC — Classificador de Lesões Bucais (EfficientNetV2-M)')
plt.legend(loc='lower right')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('roc_5classes_lesoes.png', dpi=150)

model.save('modelos/classificador_lesoes_bucais_5classes.h5')
print("\nModelo salvo em: modelos/classificador_lesoes_bucais_5classes.h5")
