import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QCheckBox, QSlider, 
                             QGroupBox, QFileDialog, QGridLayout, QSpinBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont

class ShapeDetectorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Détecteur de Formes Géométriques")
        self.setGeometry(100, 100, 1200, 800)
        
        # Variables pour la caméra et l'image
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_image = None
        self.original_image = None
        
        # Paramètres de détection
        self.detect_circles = True
        self.detect_rectangles = True
        self.detect_triangles = True
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Panel de contrôle (gauche)
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
        # Zone d'affichage de l'image (droite)
        image_layout = QVBoxLayout()
        
        # Label pour afficher l'image
        self.image_label = QLabel()
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("border: 2px solid gray; background-color: #f0f0f0;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Chargez une image ou activez la caméra")
        
        # Label pour les statistiques
        self.stats_label = QLabel("Statistiques: Aucune détection")
        self.stats_label.setFont(QFont("Arial", 10))
        self.stats_label.setStyleSheet("padding: 10px; background-color: #e0e0e0; border-radius: 5px;")
        
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.stats_label)
        
        main_layout.addLayout(image_layout, 2)
        
    def create_control_panel(self):
        panel = QWidget()
        panel.setMaximumWidth(300)
        layout = QVBoxLayout(panel)
        
        # Titre
        title = QLabel("Contrôles de Détection")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Boutons de contrôle principal
        main_controls = QGroupBox("Contrôles Principaux")
        main_layout = QVBoxLayout(main_controls)
        
        self.load_image_btn = QPushButton("📁 Charger une Image")
        self.load_image_btn.clicked.connect(self.load_image)
        self.load_image_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 12px; }")
        
        self.camera_btn = QPushButton("📷 Activer/Désactiver Caméra")
        self.camera_btn.clicked.connect(self.toggle_camera)
        self.camera_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 12px; }")
        
        main_layout.addWidget(self.load_image_btn)
        main_layout.addWidget(self.camera_btn)
        
        # Types de formes à détecter
        shapes_group = QGroupBox("Formes à Détecter")
        shapes_layout = QVBoxLayout(shapes_group)
        
        self.circles_check = QCheckBox("🔵 Cercles")
        self.circles_check.setChecked(True)
        self.circles_check.stateChanged.connect(lambda: setattr(self, 'detect_circles', self.circles_check.isChecked()))
        
        self.rectangles_check = QCheckBox("🟦 Rectangles")
        self.rectangles_check.setChecked(True)
        self.rectangles_check.stateChanged.connect(lambda: setattr(self, 'detect_rectangles', self.rectangles_check.isChecked()))
        
        self.triangles_check = QCheckBox("🔺 Triangles")
        self.triangles_check.setChecked(True)
        self.triangles_check.stateChanged.connect(lambda: setattr(self, 'detect_triangles', self.triangles_check.isChecked()))
        
        shapes_layout.addWidget(self.circles_check)
        shapes_layout.addWidget(self.rectangles_check)
        shapes_layout.addWidget(self.triangles_check)
        
        # Bouton de traitement manuel
        process_btn = QPushButton("🔄 Retraiter l'Image")
        process_btn.clicked.connect(self.process_current_image)
        process_btn.setStyleSheet("QPushButton { padding: 8px; font-size: 11px; background-color: #4CAF50; color: white; }")
        
        # Ajouter tous les groupes au layout principal
        layout.addWidget(main_controls)
        layout.addWidget(shapes_group)
        layout.addWidget(process_btn)
        layout.addStretch()
        
        return panel
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Charger une Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if file_path:
            # Arrêter la caméra si elle est active
            if self.cap and self.cap.isOpened():
                self.cap.release()
                self.timer.stop()
                
            # Charger l'image
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.current_image = self.original_image.copy()
                self.process_current_image()
                
    def toggle_camera(self):
        if self.cap is None or not self.cap.isOpened():
            # Activer la caméra
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.timer.start(30)  # 30ms = ~33 FPS
                self.camera_btn.setText("📷 Désactiver Caméra")
            else:
                self.image_label.setText("Erreur: Impossible d'accéder à la caméra")
        else:
            # Désactiver la caméra
            self.cap.release()
            self.timer.stop()
            self.camera_btn.setText("📷 Activer Caméra")
            self.image_label.setText("Caméra désactivée")
            
    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_image = frame
                self.process_current_image()
                
    def find_circles(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        
        # Paramètres optimisés pour la détection de cercles
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 
            dp=1,                    # Résolution inverse
            minDist=50,             # Distance minimale entre cercles
            param1=50,              # Seuil pour la détection de contours
            param2=30,              # Seuil pour les centres
            minRadius=10,           # Rayon minimum
            maxRadius=100           # Rayon maximum
        )
        
        detected_circles = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(image, (x, y), r, (0, 255, 0), 3)      # Cercle en vert
                cv2.circle(image, (x, y), 2, (0, 0, 255), 3)      # Centre en rouge
                detected_circles.append((x, y, r))
                
        return detected_circles
        
    def find_rectangles_and_triangles(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Trouver les contours pour détecter les formes
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        triangles = []
        
        for contour in contours:
            # Approximation polygonale
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Filtrer par aire minimale
            area = cv2.contourArea(contour)
            if area < 500:  # Ignorer les petites formes
                continue
                
            # Classification basée sur le nombre de sommets
            if len(approx) == 3 and self.detect_triangles:
                # Triangle en bleu
                cv2.drawContours(image, [approx], -1, (255, 0, 0), 3)
                triangles.append(approx)
                
            elif len(approx) == 4 and self.detect_rectangles:
                # Rectangle en rouge
                cv2.drawContours(image, [approx], -1, (0, 0, 255), 3)
                rectangles.append(approx)
                
        return rectangles, triangles
        
    def process_current_image(self):
        if self.current_image is None:
            return
            
        # Copier l'image pour le traitement
        processed_image = self.current_image.copy()
        
        # Statistiques de détection
        circles_count = 0
        rectangles_count = 0
        triangles_count = 0
        
        # Détecter les cercles
        if self.detect_circles:
            circles = self.find_circles(processed_image)
            circles_count = len(circles)
            
        # Détecter les rectangles et triangles
        rectangles, triangles = self.find_rectangles_and_triangles(processed_image)
        rectangles_count = len(rectangles)
        triangles_count = len(triangles)
        
        # Mettre à jour les statistiques
        stats_text = f"Détections: 🔵 {circles_count} cercles, 🟦 {rectangles_count} rectangles, 🔺 {triangles_count} triangles"
        self.stats_label.setText(stats_text)
        
        # Afficher l'image traitée
        self.display_image(processed_image)
        
    def display_image(self, image):
        # Redimensionner l'image si nécessaire
        height, width, channel = image.shape
        label_width = self.image_label.width()
        label_height = self.image_label.height() - 50  # Laisser de l'espace pour le texte
        
        # Calculer le ratio pour conserver les proportions
        ratio = min(label_width/width, label_height/height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        resized_image = cv2.resize(image, (new_width, new_height))
        
        # Convertir BGR vers RGB
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        
        # Convertir en QImage puis QPixmap
        qt_image = QImage(rgb_image.data, new_width, new_height, 
                         new_width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        self.image_label.setPixmap(pixmap)
        
    def closeEvent(self, event):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Style moderne
    
    window = ShapeDetectorApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()