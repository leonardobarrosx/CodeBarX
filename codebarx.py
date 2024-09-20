import sys
import random
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QSpinBox, 
                             QProgressBar, QScrollArea, QCheckBox, QGridLayout, QRadioButton, QGroupBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from ean_list import *  # Importar a lista de EANs

class BarcodeGeneratorThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, count_1_to_5, count_6_to_9, prefix, save_path, barcode_format):
        super().__init__()
        self.count_1_to_5 = count_1_to_5
        self.count_6_to_9 = count_6_to_9
        self.prefix = prefix
        self.save_path = save_path
        self.barcode_format = barcode_format

    def generate_barcodes(self, count, first_digit_range):
        barcodes = []
        code_format = barcode.get_barcode_class(self.barcode_format)
        
        for _ in range(count):
            ean = random.choice(ean_list)
            first_digit = random.randint(*first_digit_range)
            second_digit = random.randint(*first_digit_range)
            barcode_data = f"$${first_digit}{second_digit}{ean}"

            buffer = BytesIO()
            barcode_obj = code_format(barcode_data, writer=ImageWriter())
            barcode_obj.write(buffer)
            barcodes.append((barcode_data, ean, buffer.getvalue()))

            yield barcodes[-1], int((len(barcodes) / (self.count_1_to_5 + self.count_6_to_9)) * 100)

    def run(self):
        barcodes = []
        total_count = self.count_1_to_5 + self.count_6_to_9
        
        # Generate barcodes for 1-5 range
        for barcode_data, progress in self.generate_barcodes(self.count_1_to_5, (1, 5)):
            barcodes.append(barcode_data)
            self.progress.emit(int((len(barcodes) / total_count) * 100))

        # Generate barcodes for 6-9 range
        for barcode_data, progress in self.generate_barcodes(self.count_6_to_9, (6, 9)):
            barcodes.append(barcode_data)
            self.progress.emit(int((len(barcodes) / total_count) * 100))

        self.finished.emit(barcodes)

class BarcodeGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Código de Barras")
        self.setGeometry(100, 100, 600, 500)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Input fields
        self.count_1_to_5, self.count_6_to_9 = self.create_spin_boxes()
        self.prefix = self.create_line_edit("barcode_")

        # Group box for barcode format selection
        self.barcode_format_group = QGroupBox("Formato do Código de Barras")
        self.barcode_format_layout = QHBoxLayout()

        self.code128_radio = QRadioButton("Code 128")
        self.code39_radio = QRadioButton("Code 39")
        self.code128_radio.setChecked(True)  # Default selection

        self.barcode_format_layout.addWidget(self.code128_radio)
        self.barcode_format_layout.addWidget(self.code39_radio)
        self.barcode_format_group.setLayout(self.barcode_format_layout)

        layout.addWidget(self.barcode_format_group)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Quantidade (1 a 5):"))  # Adiciona o rótulo
        input_layout.addWidget(self.count_1_to_5)  # Adiciona o spin box
        input_layout.addWidget(QLabel("Quantidade (6 a 9):"))  # Adiciona o rótulo
        input_layout.addWidget(self.count_6_to_9)  # Adiciona o spin box
        input_layout.addWidget(self.prefix)
        layout.addLayout(input_layout)

        # Save path
        self.save_path = QLineEdit()
        save_path_layout = QHBoxLayout()
        save_path_layout.addWidget(QLabel("Diretório para salvar:"))
        save_path_layout.addWidget(self.save_path)
        browse_button = QPushButton("Escolher...")
        browse_button.clicked.connect(self.choose_directory)
        save_path_layout.addWidget(browse_button)
        layout.addLayout(save_path_layout)

        # Generate button
        generate_button = QPushButton("Gerar Códigos de Barras")
        generate_button.clicked.connect(self.start_generation)
        layout.addWidget(generate_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Preview area
        self.preview_area = QScrollArea()
        self.preview_layout = QGridLayout()
        self.preview_widget = QWidget()
        self.preview_widget.setLayout(self.preview_layout)
        self.preview_area.setWidget(self.preview_widget)
        self.preview_area.setWidgetResizable(True)
        layout.addWidget(self.preview_area)

        # Action buttons
        self.setup_action_buttons(layout)

        self.barcodes = []

    def create_spin_boxes(self):
        spin_box_1 = QSpinBox()
        spin_box_1.setRange(0, 100)
        spin_box_2 = QSpinBox()
        spin_box_2.setRange(0, 100)
        return spin_box_1, spin_box_2  # Retornar os spin boxes

    def create_line_edit(self, default_text):
        line_edit = QLineEdit()
        line_edit.setText(default_text)
        return line_edit

    def setup_action_buttons(self, layout):
        action_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Selecionar Todos")
        self.select_all_button.clicked.connect(self.toggle_select_all)
        action_layout.addWidget(self.select_all_button)

        self.save_selected_button = QPushButton("Salvar Selecionados")
        self.save_selected_button.clicked.connect(self.save_selected)
        action_layout.addWidget(self.save_selected_button)

        self.save_all_button = QPushButton("Salvar Todos")
        self.save_all_button.clicked.connect(self.save_all)
        action_layout.addWidget(self.save_all_button)

        self.generate_again_button = QPushButton("Gerar Novamente")
        self.generate_again_button.clicked.connect(self.generate_again)
        action_layout.addWidget(self.generate_again_button)

        layout.addLayout(action_layout)

    def choose_directory(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Selecionar Diretório")
        if folder_selected:
            self.save_path.setText(folder_selected)

    def start_generation(self):
        save_path = self.save_path.text()
        if not save_path:
            QMessageBox.warning(self, "Erro", "Por favor, escolha um diretório para salvar as imagens.")
            return

        count_1_to_5 = self.count_1_to_5.value()
        count_6_to_9 = self.count_6_to_9.value()
        prefix = self.prefix.text()
        
        # Determinar o formato do código de barras selecionado
        barcode_format = "code128" if self.code128_radio.isChecked() else "code39"

        # Verificar se ao menos um código deve ser gerado
        if count_1_to_5 == 0 and count_6_to_9 == 0:
            QMessageBox.warning(self, "Erro", "Por favor, informe ao menos uma quantidade de códigos a serem gerados.")
            return

        self.generator_thread = BarcodeGeneratorThread(count_1_to_5, count_6_to_9, prefix, save_path, barcode_format)
        self.generator_thread.progress.connect(self.update_progress)
        self.generator_thread.finished.connect(self.generation_finished)
        self.generator_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def generation_finished(self, barcodes):
        self.barcodes = barcodes
        QMessageBox.information(self, "Sucesso", "Códigos de barras gerados com sucesso!")
        self.update_preview(barcodes)

    def update_preview(self, barcodes):
        self.clear_preview()
        for i, (barcode_data, ean, image_data) in enumerate(barcodes):
            hbox = QHBoxLayout()
            label = QLabel(f"Barcode: {barcode_data} - EAN: {ean}")

            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            label.setPixmap(scaled_pixmap)

            hbox.addWidget(label)
            checkbox = QCheckBox()
            hbox.addWidget(checkbox)
            self.preview_layout.addLayout(hbox, i // 4, i % 4)

        self.update_select_all_button()

    def clear_preview(self):
        for i in reversed(range(self.preview_layout.count())):
            self.preview_layout.itemAt(i).widget().setParent(None)

    def toggle_select_all(self):
        all_selected = all(self.preview_layout.itemAt(i).layout().itemAt(1).widget().isChecked() for i in range(self.preview_layout.count()))
        for i in range(self.preview_layout.count()):
            layout = self.preview_layout.itemAt(i).layout()
            checkbox = layout.itemAt(1).widget()
            checkbox.setChecked(not all_selected)
        self.update_select_all_button()

    def update_select_all_button(self):
        total = self.preview_layout.count()
        checked = sum(self.preview_layout.itemAt(i).layout().itemAt(1).widget().isChecked() for i in range(total))
        if checked == total:
            self.select_all_button.setText("Desmarcar Todos")
        elif checked == 0:
            self.select_all_button.setText("Selecionar Todos")
        else:
            self.select_all_button.setText("Inverter Seleção")

    def save_selected(self):
        save_path = self.save_path.text()
        for i in range(self.preview_layout.count()):
            layout = self.preview_layout.itemAt(i).layout()
            checkbox = layout.itemAt(1).widget()
            if checkbox.isChecked():
                barcode_data, ean = self.barcodes[i][:2]
                filename = os.path.join(save_path, f'{self.prefix.text()}{i + 1}_{barcode_data}.png')
                self.save_barcode_image(barcode_data, filename)

        QMessageBox.information(self, "Sucesso", "Códigos de barras selecionados salvos com sucesso!")

    def save_all(self):
        save_path = self.save_path.text()
        for i, (barcode_data, ean, _) in enumerate(self.barcodes):
            filename = os.path.join(save_path, f'{self.prefix.text()}{i + 1}_{barcode_data}.png')
            self.save_barcode_image(barcode_data, filename)

        QMessageBox.information(self, "Sucesso", "Todos os códigos de barras salvos com sucesso!")

    def save_barcode_image(self, barcode_data, filename):
        barcode_obj = barcode.get_barcode_class("code128" if self.code128_radio.isChecked() else "code39")(barcode_data, writer=ImageWriter())
        barcode_obj.save(filename)

    def generate_again(self):
        self.barcodes.clear()
        self.clear_preview()
        self.save_path.clear()
        self.count_1_to_5.setValue(0)
        self.count_6_to_9.setValue(0)
        self.prefix.clear()
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarcodeGeneratorApp()
    window.show()
    sys.exit(app.exec())
