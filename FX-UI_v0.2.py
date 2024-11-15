import sys
import os
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import QThread, pyqtSignal
import configparser

STYLE_SHEET = '''
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #2c3e50;
    background-color: #f0f4f8;  /* Softened background color */
}

QLabel {
    font-size: 15px;  /* Slightly increased font size */
    color: #34495e;
    padding: 5px;
}

QPushButton {
    background-color: #708090;  /* Changed button color */
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;  /* Increased padding for a more substantial feel */
    font-size: 15px;  /* Slightly increased font size */
    font-weight: 500;
    min-height: 40px;  /* Increased minimum height */
    transition: background-color 0.3s, transform 0.2s;  /* Added transition for hover effect */
}

QPushButton:hover {
    background-color: #5b6e76;  /* Darker shade for hover effect */
    transform: scale(1.05);  /* Slightly scale up on hover */
}

QPushButton:pressed {
    background-color: #4a585c;  /* Darker shade for pressed effect */
    transform: scale(0.95);  /* Scale down on press */
}

QPushButton:disabled {
    background-color: #b3d7ff;
    color: #6c757d;  /* Muted text color for disabled state */
}

QLineEdit {
    border: 1px solid #ced4da;
    border-radius: 8px;
    padding: 10px;  /* Increased padding */
    background-color: white;
    min-height: 40px;  /* Increased minimum height */
}

QLineEdit:focus {
    border: 1px solid #007AFF;  /* Change border color on focus */
    box-shadow: 0 0 5px rgba(0, 122, 255, 0.5);  /* Added shadow effect for focus */
}

QProgressBar {
    border: none;
    border-radius: 8px;
    background-color: #e9ecef;
    height: 10px;  /* Slightly increased height */
    text-align: center;
}

QProgressBar::chunk {
    background-color: #007AFF;
    border-radius: 8px;
    background: linear-gradient(to right, #4da6ff, #007AFF);  /* Gradient effect */
}

QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background-color: #e9ecef;  /* 背景颜色 */
    margin: 0px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #708090;  /* 改为#708090 */
    border: none;
    width: 20px;  /* Increased width for better usability */
    margin: -8px 0;
    border-radius: 10px;  /* Slightly rounded handle */
}

QSlider::add-page:horizontal {
    background-color: #e9ecef;
}

QSlider::sub-page:horizontal {
    background-color: #007AFF;
}

QListWidget {
    border: 1px solid #ced4da;
    border-radius: 8px;
    background-color: white;
    padding: 10px;  /* Increased padding */
}

QGroupBox {
    border: 1px solid #ced4da;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    background-color: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);  /* Added shadow for depth */
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #6c757d;
    font-size: 18px;  /* Increased font size for better visibility */
    font-weight: bold; /* Make the title bold */
}
'''



class VideoFrameExtractorThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    new_frame_extracted = pyqtSignal(str)

    def __init__(self, video_paths, output_folder, interval, use_gpu, separate_folders):
        super().__init__()
        self.video_paths = video_paths
        self.output_folder = output_folder
        self.interval = interval
        self.use_gpu = use_gpu
        self.is_paused = False
        self.separate_folders = separate_folders

    def run(self):
        for video_path in self.video_paths:
            try:
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    self.error.emit(f"Could not open video: {video_path}")
                    continue

                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps <= 0:
                    self.error.emit(f"Invalid FPS for video: {video_path}")
                    continue

                interval_frames = int(fps * self.interval)
                frame_count = 0
                extracted_count = 0

                # 根据复选框状态设置输出路径
                if self.separate_folders:
                    video_output_folder = os.path.join(self.output_folder, video_name)
                    if not os.path.exists(video_output_folder):
                        os.makedirs(video_output_folder)
                else:
                    video_output_folder = self.output_folder

                while True:
                    if self.is_paused:
                        self.msleep(100)
                        continue

                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % interval_frames == 0:
                        if self.use_gpu:

                            pass  # TODO:

                        output_path = os.path.join(
                            video_output_folder,
                            f"{video_name}_frame_{extracted_count:04d}.jpg"
                        )
                        cv2.imwrite(output_path, frame)
                        self.new_frame_extracted.emit(output_path)
                        self.progress.emit(frame_count)
                        extracted_count += 1

                    frame_count += 1

                cap.release()

            except Exception as e:
                self.error.emit(f"Error processing video {video_path}: {str(e)}")
                continue

        self.finished.emit()


class ImagePreviewDialog(QtWidgets.QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Image Preview')
        self.setModal(True)
        self.setStyleSheet(STYLE_SHEET)

        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.6), int(screen.height() * 0.6))
        self.setMaximumSize(screen.width(), screen.height())

        layout = QtWidgets.QVBoxLayout(self)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)

        close_button = QtWidgets.QPushButton('Close Preview')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.load_image(image_path)

    def load_image(self, image_path):
        pixmap = QtGui.QPixmap(image_path)

        # Convert the width and height to integers
        scaled_pixmap = pixmap.scaled(
            int(self.size().width() * 0.95),  # Convert to int
            int(self.size().height() * 0.95),  # Convert to int
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setMaximumSize(self.size())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_label.pixmap():
            # Convert the width and height to integers
            scaled_pixmap = self.image_label.pixmap().scaled(
                int(self.size().width() * 0.95),  # Convert to int
                int(self.size().height() * 0.95),  # Convert to int
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def mousePressEvent(self, event):
        # Close the dialog when clicking anywhere on it
        self.close()



class CustomListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setIconSize(QtCore.QSize(360, 360))
        self.setSpacing(15)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setWrapping(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            preview_dialog = ImagePreviewDialog(item.data(QtCore.Qt.UserRole), self)
            preview_dialog.exec_()




class VideoFrameExtractor(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.video_paths = []
        self.is_processing = False
        self.extractor_thread = None
        self.setStyleSheet(STYLE_SHEET)

        self.config = configparser.ConfigParser()
        self.config_file = 'settings.ini'
        self.load_settings()

        self.page3 = self.create_help_page()
        self.tab_widget.addTab(self.page3, "使用教程与作者简介 (Usage Guide and Author Info)")


        if not os.path.exists(self.config_file):
            self.config['Paths'] = {}
            self.save_settings()



    def load_settings(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            if 'Paths' not in self.config:
                self.config['Paths'] = {}
            self.output_folder_input.setText(self.config['Paths'].get('output_folder', ''))

    def save_settings(self):
        if 'Paths' not in self.config:
            self.config['Paths'] = {}
        self.config['Paths']['output_folder'] = self.output_folder_input.text()
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def browse_output_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_folder_input.text())
        if folder:
            self.output_folder_input.setText(folder)
            self.save_settings()

    def initUI(self):
        self.setWindowTitle('视频帧提取器 (Frame Extraction)')

        # 使用 QTabWidget 创建标签页
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.tab_widget)

        # 创建第一页：视频上传和提取设置
        self.page1 = self.create_upload_page()
        self.tab_widget.addTab(self.page1, "上传与设置 (Upload and Settings)")

        # 创建第二页：图片预览和删除
        self.page2 = self.create_preview_page()
        self.tab_widget.addTab(self.page2, "预览与删除提取的帧 (Preview and Delete Extracted Frames)")

    def create_upload_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)


        upload_group = QtWidgets.QGroupBox("视频上传 (Video Upload)")
        upload_layout = QtWidgets.QVBoxLayout()
        self.upload_button = QtWidgets.QPushButton('选择视频文件 (Select Video File)')
        upload_layout.addWidget(self.upload_button)
        self.upload_button.clicked.connect(self.upload_videos)
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)


        settings_group = QtWidgets.QGroupBox("提取设置 (Extraction Settings)")
        settings_layout = QtWidgets.QVBoxLayout()


        interval_label = QtWidgets.QLabel("帧间隔 (Frame Interval)")
        settings_layout.addWidget(interval_label)

        interval_layout = QtWidgets.QHBoxLayout()
        self.interval_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.interval_slider.setMinimum(1)
        self.interval_slider.setMaximum(100)
        self.interval_slider.setValue(10)
        self.interval_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.interval_slider.setTickInterval(10)
        interval_layout.addWidget(self.interval_slider)

        self.interval_label = QtWidgets.QLabel('1.0秒 (1.0s)')
        interval_layout.addWidget(self.interval_label)
        settings_layout.addLayout(interval_layout)

        self.interval_slider.valueChanged.connect(self.update_interval_label)


        self.gpu_acceleration_checkbox = QtWidgets.QCheckBox("启用 GPU 加速 (Enable GPU Acceleration)（waiting...）")
        settings_layout.addWidget(self.gpu_acceleration_checkbox)


        output_label = QtWidgets.QLabel("输出目录 (Output Directory)")
        settings_layout.addWidget(output_label)

        folder_layout = QtWidgets.QHBoxLayout()
        self.output_folder_input = QtWidgets.QLineEdit()
        self.output_folder_input.setPlaceholderText('选择输出文件夹... (Select Output Folder...)')
        folder_layout.addWidget(self.output_folder_input)

        self.browse_button = QtWidgets.QPushButton('浏览 (Browse)')
        self.browse_button.clicked.connect(self.browse_output_folder)
        folder_layout.addWidget(self.browse_button)
        settings_layout.addLayout(folder_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)


        self.separate_folders_checkbox = QtWidgets.QCheckBox(
            "批量处理时，按照不同的视频保存到对应的文件夹 (Separate folders for each video)")  # 复选框文本
        settings_layout.addWidget(self.separate_folders_checkbox)


        control_group = QtWidgets.QGroupBox("控制 (Control)")
        control_layout = QtWidgets.QVBoxLayout()

        self.extract_button = QtWidgets.QPushButton('提取帧 (Extract Frames)')
        self.extract_button.clicked.connect(self.extract_frames)
        control_layout.addWidget(self.extract_button)

        self.pause_button = QtWidgets.QPushButton('暂停 (Pause)')
        self.pause_button.clicked.connect(self.toggle_pause)
        control_layout.addWidget(self.pause_button)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        page.setLayout(layout)
        return page

    def create_preview_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)


        gallery_group = QtWidgets.QGroupBox("提取的帧 (Extracted Frames) (双击预览大图，点击或者勾画选中一个区域的图片，然后点击删除按钮) (Double-click to preview large image, click or select a region to delete)")  # 修改组框标题为中英双语
        gallery_layout = QtWidgets.QVBoxLayout()

        self.gallery = CustomListWidget()
        gallery_layout.addWidget(self.gallery)

        self.delete_button = QtWidgets.QPushButton('删除选中的帧 (Delete Selected Frames)')
        self.delete_button.clicked.connect(self.delete_selected_images)
        gallery_layout.addWidget(self.delete_button)

        gallery_group.setLayout(gallery_layout)
        layout.addWidget(gallery_group)

        page.setLayout(layout)
        return page




    def switch_to_preview(self):
        self.stacked_widget.setCurrentWidget(self.page2)

    def toggle_pause(self):
        if self.extractor_thread:
            self.extractor_thread.is_paused = not self.extractor_thread.is_paused
            self.pause_button.setText('Resume' if self.extractor_thread.is_paused else 'Pause')


    def create_thumbnail(self, image_path):
        try:
            image = QtGui.QImage(image_path)
            if image.isNull():
                return None
            # 设定缩略图的大小
            scaled_image = image.scaled(360, 360, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            return QtGui.QIcon(QtGui.QPixmap.fromImage(scaled_image))
        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return None

    def add_gallery_item(self, image_path):
        try:
            item = QtWidgets.QListWidgetItem()
            thumbnail = self.create_thumbnail(image_path)
            if thumbnail:
                item.setIcon(thumbnail)


            file_name = os.path.basename(image_path)
            if len(file_name) > 20:
                file_name = file_name[:17] + '...'

            item.setText(file_name)
            item.setData(QtCore.Qt.UserRole, image_path)


            item.setSizeHint(QtCore.QSize(360, 220))

            self.gallery.addItem(item)
        except Exception as e:
            print(f"Error adding gallery item: {str(e)}")

    def update_interval_label(self, value):
        self.interval_label.setText(f'{value / 10:.1f}s')
    def create_help_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()


        tutorial_text = (
            "<h2>软件使用教程</h2>"
            "<p>1. 选择视频文件。</p>"
            "<p>2. 设置帧间隔。</p>"
            "<p>3. 选择输出目录。</p>"
            "<p>3. 若希望在批量处理的时候，根据不同的视频将提取的帧保存在不同的文件夹，则勾选批量处理分文件夹。</p>"
            "<p>4. 点击提取帧按钮开始提取。</p>"
            "<p>5. 在预览页面中查看提取的帧，可以双击查看大图片，点击图片任意地方结束大图预览，单机勾选图片，点击删除按钮后执行删除。</p>"
            "<p>6. 可以删除不需要的帧。</p>"
            "<h2>作者简介</h2>"
            "<p>Kuie，b站主页：https://space.bilibili.com/3546720325601780?spm_id_from=333.1007.0.0</p>"
            "<p>2. 用于计算机视觉图片预处理</p>"
        )

        tutorial_label = QtWidgets.QLabel()
        tutorial_label.setText(tutorial_text)
        tutorial_label.setWordWrap(True)  # 自动换行
        layout.addWidget(tutorial_label)

        page.setLayout(layout)
        return page
    def browse_output_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.output_folder_input.setText(folder)

    def upload_videos(self):
        try:
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.ReadOnly
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self,
                "Select Video Files",
                "",
                "Video Files (*.mp4 *.avi *.mov);;All Files (*)",
                options=options
            )
            if files:
                self.video_paths = files

                self.config['Paths']['input_folder'] = os.path.dirname(files[0])
                self.save_settings()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error selecting files: {str(e)}")

    def extract_frames(self):
        if self.is_processing:
            return

        if not self.video_paths:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select video files first")
            return

        output_folder = self.output_folder_input.text()
        if not output_folder:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please specify output folder")
            return

        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not create output folder: {str(e)}")
            return

        self.is_processing = True
        self.progress_bar.setVisible(True)
        self.extract_button.setEnabled(False)
        self.gallery.clear()

        interval = self.interval_slider.value() / 10
        use_gpu = self.gpu_acceleration_checkbox.isChecked()


        self.extractor_thread = VideoFrameExtractorThread(self.video_paths, output_folder, interval, use_gpu,
                                                          self.separate_folders_checkbox.isChecked())
        self.extractor_thread.progress.connect(self.update_progress)
        self.extractor_thread.finished.connect(self.on_finished)
        self.extractor_thread.error.connect(self.show_error)
        self.extractor_thread.new_frame_extracted.connect(self.add_gallery_item)
        self.extractor_thread.start()

    def update_progress(self, frame_count):
        self.progress_bar.setValue(frame_count)

    def on_finished(self):
        self.is_processing = False
        self.progress_bar.setVisible(False)
        self.extract_button.setEnabled(True)

    def show_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Error", message)

    def process_videos(self, output_folder):
        interval = self.interval_slider.value() / 10
        use_gpu = self.gpu_acceleration_checkbox.isChecked()

        for video_path in self.video_paths:
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    QtWidgets.QMessageBox.warning(self, "Warning", f"Could not open video: {video_path}")
                    continue

                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps <= 0:
                    QtWidgets.QMessageBox.warning(self, "Warning", f"Invalid FPS for video: {video_path}")
                    continue

                interval_frames = int(fps * interval)
                frame_count = 0
                extracted_count = 0

                self.progress_bar.setMaximum(total_frames)

                while True:
                    if self.is_paused:
                        QtWidgets.QApplication.processEvents()
                        continue  # 暂停处理

                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % interval_frames == 0:
                        if use_gpu:

                            pass  # TODO:

                        output_path = os.path.join(
                            output_folder,
                            f"{os.path.splitext(os.path.basename(video_path))[0]}_frame_{extracted_count:04d}.jpg"
                        )
                        cv2.imwrite(output_path, frame)
                        self.add_gallery_item(output_path)
                        extracted_count += 1

                    frame_count += 1
                    self.progress_bar.setValue(frame_count)
                    QtWidgets.QApplication.processEvents()

                cap.release()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error processing video {video_path}: {str(e)}")
                continue

    def delete_selected_images(self):
        try:
            selected_items = self.gallery.selectedItems()
            if not selected_items:
                return

            # Directly delete selected images without confirmation
            deleted_count = 0
            for item in selected_items:
                img_path = item.data(QtCore.Qt.UserRole)
                try:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                        deleted_count += 1
                        self.gallery.takeItem(self.gallery.row(item))
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Warning", f"Could not delete {img_path}: {str(e)}")

            # Removed the message box that indicates the number of deleted images
            # QtWidgets.QMessageBox.information(self, "Success", f"Deleted {deleted_count} images")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error during deletion: {str(e)}")
if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        extractor = VideoFrameExtractor()
        extractor.resize(300, 600)
        extractor.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Critical error: {str(e)}")