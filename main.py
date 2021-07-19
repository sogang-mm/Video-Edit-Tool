from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
import qtawesome as qta

from PIL import Image, ImageDraw, ImageFont
import subprocess
import json

from core import Core, ImageHelper, pQueue
from canvas import Canvas
from config import *


class VideoEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.check_ffmpeg()
        self.core = Core()

    def initUI(self):

        # APP Layout
        # layout = QHBoxLayout()
        layout = QGridLayout()

        self.progressbar = QProgressBar(self)
        ##############################################
        # Input
        ##############################################
        self.input_panel = QWidget(self)

        # Video input buttons
        buttons = QWidget(self)
        btn_add = QPushButton(qta.icon('fa5s.file-video',
                                       options=[{'scale_factor': 1}]), '')
        btn_add.setToolTip('Append Videos.')

        btn_add_all = QPushButton(qta.icon('fa5s.folder',
                                           options=[{'scale_factor': 1}]), '')
        btn_add_all.setToolTip('Append all the videos in the subdirectory.')

        btn_remove = QPushButton(qta.icon('fa5s.minus-square',
                                          options=[{'scale_factor': 1}]), '')
        btn_remove.setToolTip('Remove a selected video.')

        btn_clear = QPushButton(qta.icon('fa5s.trash',
                                         options=[{'scale_factor': 1}]), '')
        btn_clear.setToolTip('Clear video list.')

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_add_all)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_clear)

        buttons.setLayout(btn_layout)

        # Video Table
        self.table = QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderLabels(['name', 'path'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.table.setTextElideMode(Qt.ElideNone)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        input_panel_layout = QVBoxLayout()
        input_panel_layout.addWidget(buttons)
        input_panel_layout.addWidget(self.table)

        self.input_panel.setLayout(input_panel_layout)

        ##############################################
        # Viewer
        ##############################################
        self.viewer = QWidget()

        # Preview canvas
        self.canvas = Canvas()

        # Video info
        self.info = QGroupBox()
        self.info_label_name = QLabel('Name: ')
        self.info_label_path = QLabel('Path: ')
        self.info_label_duration = QLabel('Duration: ')
        self.info_label_fps = QLabel('Frame Rate: ')
        self.info_label_count = QLabel('Frame Count: ')
        self.info_label_size = QLabel('Resolution: ')

        self.info_name = QLabel()
        self.info_path = QLabel()
        self.info_duration = QLabel()
        self.info_fps = QLabel()
        self.info_count = QLabel()
        self.info_size = QLabel()

        info_layout = QGridLayout()
        info_layout.addWidget(self.info_label_name, 0, 0, 1, 1)
        info_layout.addWidget(self.info_name, 0, 1, 1, 3)

        info_layout.addWidget(self.info_label_path, 1, 0)
        info_layout.addWidget(self.info_path, 1, 1)

        info_layout.addWidget(self.info_label_duration, 2, 0)
        info_layout.addWidget(self.info_duration, 2, 1)

        info_layout.addWidget(self.info_label_fps, 3, 0)
        info_layout.addWidget(self.info_fps, 3, 1)

        info_layout.addWidget(self.info_label_count, 4, 0)
        info_layout.addWidget(self.info_count, 4, 1)

        info_layout.addWidget(self.info_label_size, 5, 0)
        info_layout.addWidget(self.info_size, 5, 1)

        self.info.setLayout(info_layout)

        viewer_layout = QVBoxLayout()
        viewer_layout.addWidget(self.canvas)
        viewer_layout.addWidget(self.info)

        self.viewer.setLayout(viewer_layout)

        ##############################################
        # Controls
        ##############################################
        self.controls = QWidget()
        self.controls.setEnabled(False)

        # Transforms
        self.transforms = QGroupBox('Transformations')
        transform_layout = QGridLayout()

        # Transforms - preset
        self.preset = QGroupBox('Preset')
        self.preset_edit_path = QLineEdit()
        self.preset_edit_path.setReadOnly(True)
        preset_btn_load = QToolButton()
        preset_btn_load.setIcon(qta.icon('fa5s.file-import',
                                         options=[{'scale_factor': 1}]))
        preset_btn_load.setToolTip('Load preset file.')

        preset_btn_save = QToolButton()
        preset_btn_save.setIcon(qta.icon('fa5s.save',
                                         options=[{'scale_factor': 1}]))
        preset_btn_save.setToolTip('Save preset file.')

        preset_layout = QGridLayout()
        preset_layout.addWidget(self.preset_edit_path, 0, 0, 1, 3)
        preset_layout.addWidget(preset_btn_load, 0, 4, 1, 1)
        preset_layout.addWidget(preset_btn_save, 0, 5, 1, 1)

        self.preset.setLayout(preset_layout)
        self.transforms.setLayout(transform_layout)

        # Transforms - Brightness
        brightness_group = QGroupBox('Brightness')
        self.brightness = QComboBox()
        self.brightness.addItems(['-36', '-18', '-9', '0', '+9', '+18', '+36'])
        self.brightness.setCurrentIndex(3)

        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(self.brightness)
        brightness_group.setLayout(brightness_layout)

        # Transforms - Contrast
        contrast_group = QGroupBox('Contrast')
        self.contrast = QComboBox()
        self.contrast.addItems(['-20', '0', '+20'])
        self.contrast.setCurrentIndex(1)

        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(self.contrast)
        contrast_group.setLayout(contrast_layout)

        # Transforms - Flip
        flip_group = QGroupBox('Flip')
        self.flip = QComboBox()
        self.flip.addItems(['None', 'Horizontal', 'Vertical', 'All'])
        self.flip.setCurrentIndex(0)

        flip_layout = QHBoxLayout()
        flip_layout.addWidget(self.flip)
        flip_group.setLayout(flip_layout)

        # Transforms - Rotation
        rotation_group = QGroupBox('Rotation')
        self.rotation = QComboBox()
        self.rotation.addItems(['0', '90', '180', '270'])
        self.rotation.setCurrentIndex(0)

        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(self.rotation)
        rotation_group.setLayout(rotation_layout)

        # Transforms - Frame rate
        framerate_group = QGroupBox('Frame Rate')
        self.framerate = QComboBox()
        self.framerate.addItems(['None', '5 fps', '10 fps', '20 fps'])
        self.framerate.setCurrentIndex(0)

        framerate_layout = QHBoxLayout()
        framerate_layout.addWidget(self.framerate)
        framerate_group.setLayout(framerate_layout)

        # Transforms - Grayscale
        grayscale_group = QGroupBox('Grayscale')
        self.grayscale = QComboBox()
        self.grayscale.addItems(['OFF', 'ON'])
        self.grayscale.setCurrentIndex(0)

        grayscale_layout = QHBoxLayout()
        grayscale_layout.addWidget(self.grayscale)
        grayscale_group.setLayout(grayscale_layout)

        # Transforms - Logo
        self.logo_group = QGroupBox('Logo')
        self.logo_group.setCheckable(True)
        self.logo_group.setChecked(False)

        self.logo_path = QLineEdit(LOGO_DEFAULT)
        self.logo_path.setReadOnly(True)
        self.logo_path_button = QToolButton()
        self.logo_reset_button = QToolButton()
        self.logo_reset_button.setIcon(qta.icon('fa5s.sync-alt',
                                                options=[{'scale_factor': 1}]))
        self.logo_reset_button.setToolTip('Load default logo image.')
        self.logo_path_button.setIcon(qta.icon('ei.folder-open',
                                               options=[{'scale_factor': 1}]))
        self.logo_path_button.setToolTip('Browse logo image.')

        self.logo_size = QComboBox()
        self.logo_size.addItems(['10 %', '20 %', '30 %'])

        self.logo_x_slider = QSlider(Qt.Horizontal)
        self.logo_x_slider.setRange(0, 100)
        self.logo_x_slider.setValue(50)
        self.logo_x_slider.setSingleStep(5)
        self.logo_x_slider_label = QLabel(f'{50:4} %')
        self.logo_x_slider_label.setAlignment(Qt.AlignCenter)

        self.logo_y_slider = QSlider(Qt.Horizontal)
        self.logo_y_slider.setRange(0, 100)
        self.logo_y_slider.setValue(50)
        self.logo_y_slider.setSingleStep(5)
        self.logo_y_slider_label = QLabel(f'{50:4} %')
        self.logo_y_slider_label.setAlignment(Qt.AlignCenter)

        logo_layout = QGridLayout()
        logo_layout.addWidget(QLabel('Path'), 0, 0, 1, 1)
        logo_layout.addWidget(self.logo_path, 0, 1, 1, 3)
        logo_layout.addWidget(self.logo_path_button, 0, 4, 1, 1)
        logo_layout.addWidget(self.logo_reset_button, 0, 5, 1, 1)

        logo_layout.addWidget(QLabel('Size'), 1, 0, 1, 1)
        logo_layout.addWidget(self.logo_size, 1, 1, 1, 5)

        logo_layout.addWidget(QLabel('X'), 2, 0, 1, 1)
        logo_layout.addWidget(self.logo_x_slider, 2, 1, 1, 4)
        logo_layout.addWidget(self.logo_x_slider_label, 2, 5, 1, 1)

        logo_layout.addWidget(QLabel('Y'), 3, 0, 1, 1)
        logo_layout.addWidget(self.logo_y_slider, 3, 1, 1, 4)
        logo_layout.addWidget(self.logo_y_slider_label, 3, 5, 1, 1)

        self.logo_group.setLayout(logo_layout)

        # Transforms - caption
        self.caption_group = QGroupBox('Caption')
        self.caption_group.setCheckable(True)
        self.caption_group.setChecked(False)

        self.caption_size = QComboBox()
        self.caption_size.addItems(['12 pt', '16 pt', '20 pt'])
        self.caption_input = QLineEdit()
        self.caption_save = QToolButton()
        self.caption_save.setIcon(qta.icon('fa5s.save',
                                           options=[{'scale_factor': 1}]))
        self.caption_color = QToolButton()
        self.caption_color.setStyleSheet('QWidget { background-color: %s }' % CAPTION_COLOR_DEFAULT)

        self.caption_x_slider = QSlider(Qt.Horizontal)
        self.caption_x_slider.setRange(0, 100)
        self.caption_x_slider.setValue(50)
        self.caption_x_slider.setSingleStep(5)
        self.caption_x_slider_label = QLabel(f'{50:4} %')
        self.caption_x_slider_label.setAlignment(Qt.AlignCenter)

        self.caption_y_slider = QSlider(Qt.Horizontal)
        self.caption_y_slider.setRange(0, 100)
        self.caption_y_slider.setValue(75)
        self.caption_y_slider.setSingleStep(5)
        self.caption_y_slider_label = QLabel(f'{75:4} %')
        self.caption_y_slider_label.setAlignment(Qt.AlignCenter)

        caption_layout = QGridLayout()
        caption_layout.addWidget(QLabel('Font'), 0, 0, 1, 1)
        caption_layout.addWidget(self.caption_size, 0, 1, 1, 4)
        caption_layout.addWidget(self.caption_color, 0, 5, 1, 1)

        caption_layout.addWidget(QLabel('Text'), 1, 0, 1, 1)
        caption_layout.addWidget(self.caption_input, 1, 1, 1, 5)

        caption_layout.addWidget(QLabel('X'), 2, 0, 1, 1)
        caption_layout.addWidget(self.caption_x_slider, 2, 1, 1, 4)
        caption_layout.addWidget(self.caption_x_slider_label, 2, 5, 1, 1)

        caption_layout.addWidget(QLabel('Y'), 3, 0, 1, 1)
        caption_layout.addWidget(self.caption_y_slider, 3, 1, 1, 4)
        caption_layout.addWidget(self.caption_y_slider_label, 3, 5, 1, 1)

        self.caption_group.setLayout(caption_layout)

        # Transforms - Camcording camcording

        self.camcording_group = QGroupBox('Camcording')
        self.camcording_group.setCheckable(True)
        self.camcording_group.setChecked(False)

        self.camcording_path = QLineEdit(CAMCORDING_DEFAULT)
        self.camcording_path.setReadOnly(True)
        self.camcording_path_button = QToolButton()
        self.camcording_reset_button = QToolButton()
        self.camcording_reset_button.setIcon(qta.icon('fa5s.sync-alt',
                                                options=[{'scale_factor': 1}]))
        self.camcording_reset_button.setToolTip('Load default logo image.')
        self.camcording_path_button.setIcon(qta.icon('ei.folder-open',
                                               options=[{'scale_factor': 1}]))
        self.camcording_path_button.setToolTip('Browse logo image.')

        self.camcording_slider = QSlider(Qt.Horizontal)
        self.camcording_slider.setRange(50, 100)
        self.camcording_slider.setValue(75)
        self.camcording_slider.setSingleStep(5)
        self.camcording_slider_label = QLabel(f'{75:4} %')
        self.camcording_slider_label.setAlignment(Qt.AlignCenter)

        camcording_layout = QGridLayout()
        camcording_layout.addWidget(QLabel('Path'), 0, 0, 1, 1)
        camcording_layout.addWidget(self.camcording_path, 0, 1, 1, 3)
        camcording_layout.addWidget(self.camcording_path_button, 0, 4, 1, 1)
        camcording_layout.addWidget(self.camcording_reset_button, 0, 5, 1, 1)
        camcording_layout.addWidget(QLabel('length ratio'), 1, 0, 1, 1)
        camcording_layout.addWidget(self.camcording_slider, 1, 1, 1, 4)
        camcording_layout.addWidget(self.camcording_slider_label, 1, 5, 1, 1)

        self.camcording_group.setLayout(camcording_layout)

        # Transforms - Border
        self.border_group = QGroupBox('Border')
        self.border_group.setCheckable(True)
        self.border_group.setChecked(False)
        border_layout = QGridLayout()

        self.border_w_slider = QSlider(Qt.Horizontal)
        self.border_w_slider.setRange(0, 50)
        self.border_w_slider_label = QLabel(f'{0:4} %')
        self.border_w_slider_label.setAlignment(Qt.AlignCenter)

        self.border_h_slider = QSlider(Qt.Horizontal)
        self.border_h_slider.setRange(0, 50)
        self.border_h_slider_label = QLabel(f'{0:4} %')
        self.border_h_slider_label.setAlignment(Qt.AlignCenter)

        border_layout.addWidget(QLabel('Width'), 0, 0)
        border_layout.addWidget(self.border_w_slider, 0, 1, 1, 3)
        border_layout.addWidget(self.border_w_slider_label, 0, 4, 1, 1)
        border_layout.addWidget(QLabel('Height'), 1, 0)
        border_layout.addWidget(self.border_h_slider, 1, 1, 1, 3)
        border_layout.addWidget(self.border_h_slider_label, 1, 4, 1, 1)
        self.border_group.setLayout(border_layout)

        # Transforms - Crop
        self.crop_group = QGroupBox('Crop')
        self.crop_group.setCheckable(True)
        self.crop_group.setChecked(False)

        self.crop_slider = QSlider(Qt.Horizontal)
        self.crop_slider.setRange(0, 50)
        self.crop_slider_label = QLabel(f'{0:4} %')
        self.crop_slider_label.setAlignment(Qt.AlignCenter)

        crop_layout = QGridLayout()
        crop_layout.addWidget(QLabel('Ratio'), 0, 0)
        crop_layout.addWidget(self.crop_slider, 0, 1, 1, 3)
        crop_layout.addWidget(self.crop_slider_label, 0, 4, 1, 1)
        self.crop_group.setLayout(crop_layout)

        # Transforms - Resolution
        self.resolution_group = QGroupBox('Resolution')
        self.resolution_group.setCheckable(True)
        self.resolution_group.setChecked(False)

        self.resolution_ratio = QRadioButton('Ratio')
        self.resolution_ratio.setChecked(True)
        self.resolution_ratio_combobox = QComboBox()
        self.resolution_ratio_combobox.addItems(['-30 %', '-20 %', '-10 %', '+10 %', '+20 %', '+30 %'])

        self.resolution_preset = QRadioButton('Preset')
        self.resolution_preset_combobox = QComboBox()
        self.resolution_preset_combobox.addItems(['QCIF', 'CIF', 'SD', 'HD', '4K-UHD'])

        self.resolution_value = QRadioButton('Value')
        self.resolution_value_w = QLineEdit('')
        self.resolution_value_w.setValidator(QIntValidator(1, 9999))
        self.resolution_value_h = QLineEdit('')
        self.resolution_value_h.setValidator(QIntValidator(1, 9999))

        resolution_layout = QGridLayout()
        resolution_layout.addWidget(self.resolution_ratio, 0, 0, 1, 1, )
        resolution_layout.addWidget(self.resolution_ratio_combobox, 0, 1, 1, 5, )
        resolution_layout.addWidget(self.resolution_preset, 1, 0, 1, 1)
        resolution_layout.addWidget(self.resolution_preset_combobox, 1, 1, 1, 5, )
        resolution_layout.addWidget(self.resolution_value, 2, 0, 1, 1)
        resolution_layout.addWidget(QLabel('W'), 2, 1, 1, 1)
        resolution_layout.addWidget(self.resolution_value_w, 2, 2, 1, 1)
        resolution_layout.addWidget(QLabel('H'), 2, 3, 1, 1)
        resolution_layout.addWidget(self.resolution_value_h, 2, 4, 1, 1)

        self.resolution_group.setLayout(resolution_layout)

        # Transform - Reset
        reset_btn = QPushButton('Reset')

        transform_layout.addWidget(self.preset, 1, 0, 1, 2)
        transform_layout.addWidget(brightness_group, 2, 0, 1, 1)
        transform_layout.addWidget(contrast_group, 2, 1, 1, 1)

        transform_layout.addWidget(flip_group, 3, 0, 1, 1)
        transform_layout.addWidget(rotation_group, 3, 1, 1, 1)

        transform_layout.addWidget(framerate_group, 4, 0, 1, 1)
        transform_layout.addWidget(grayscale_group, 4, 1, 1, 1)

        transform_layout.addWidget(self.logo_group, 5, 0, 1, 2)
        transform_layout.addWidget(self.caption_group, 6, 0, 1, 2)
        transform_layout.addWidget(self.camcording_group, 7, 0, 1, 2)
        transform_layout.addWidget(self.border_group, 8, 0, 1, 2)
        transform_layout.addWidget(self.crop_group, 9, 0, 1, 2)
        transform_layout.addWidget(self.resolution_group, 10, 0, 1, 2)
        transform_layout.addWidget(reset_btn, 11, 1, 1, 1)

        # transform_layout.addWidget(self.border_group, 6, 0, 1, 2)
        # transform_layout.addWidget(self.crop_group, 7, 0, 1, 2)
        # transform_layout.addWidget(self.resolution_group, 8, 0, 1, 2)
        # transform_layout.addWidget(reset_btn, 9, 1, 1, 1)

        # Apply Btn
        control_btn_group = QWidget()
        self.apply_btn = QPushButton('Apply')
        self.apply_all_btn = QPushButton('Apply All')
        self.make_script_btn = QPushButton('Save Script')
        control_btn_group_layout = QHBoxLayout()

        control_btn_group_layout.addWidget(self.apply_btn)
        control_btn_group_layout.addWidget(self.apply_all_btn)
        control_btn_group_layout.addWidget(self.make_script_btn)
        control_btn_group.setLayout(control_btn_group_layout)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.transforms)
        control_layout.addWidget(control_btn_group)

        self.controls.setLayout(control_layout)
        layout.addWidget(self.progressbar, 0, 0, 1, 2)
        layout.addWidget(self.input_panel, 1, 0)
        layout.addWidget(self.viewer, 1, 1)
        layout.addWidget(self.controls, 0, 2, 2, 1)
        self.setLayout(layout)

        ##############################################
        # configure
        ##############################################

        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(WINDOW_POS_X,
                         WINDOW_POS_Y,
                         WINDOW_WIDTH,
                         WINDOW_HEIGHT)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.input_panel.setFixedWidth(VIDEO_TABLE_WIDTH)
        # self.table.setFixedWidth(VIDEO_TABLE_WIDTH)
        self.canvas.setFixedWidth(CANVAS_WIDTH)
        self.canvas.setFixedHeight(CANVAS_HEIGHT)
        self.info.setFixedWidth(INFO_WIDTH)
        self.center()  # 삭제할것

        ##############################################
        # Events
        ##############################################

        btn_add.clicked.connect(self.e_video_add_btn_clicked)
        btn_add_all.clicked.connect(self.e_video_add_all_btn_clicked)
        btn_remove.clicked.connect(self.e_video_remove_btn_clicked)
        btn_clear.clicked.connect(self.e_video_clear_btn_clicked)

        self.table.itemDoubleClicked.connect(self.e_open_video)

        preset_btn_load.clicked.connect(self.e_load_preset_btn_clicked)
        preset_btn_save.clicked.connect(self.e_save_preset_btn_clicked)
        reset_btn.clicked.connect(self.e_reset_transform)

        self.apply_btn.clicked.connect(self.e_apply_btn_clicked)
        self.apply_all_btn.clicked.connect(self.e_apply_all_btn_clicked)
        self.make_script_btn.clicked.connect(self.e_make_script_btn_clicked)

        ###
        self.brightness.currentIndexChanged.connect(self.e_brigtnessChanged)
        self.contrast.currentIndexChanged.connect(self.e_contrastChanged)
        self.flip.currentIndexChanged.connect(self.e_flipChanged)
        self.rotation.currentIndexChanged.connect(self.e_rotationChanged)
        self.framerate.currentIndexChanged.connect(self.e_framerateChanged)
        self.grayscale.currentIndexChanged.connect(self.e_grayscaleChanged)

        self.logo_group.clicked.connect(self.e_logoChanged)
        self.logo_path_button.clicked.connect(self.e_logo_btn_clicked)
        self.logo_reset_button.clicked.connect(self.e_logo_reset_btn_clicked)

        self.logo_path.textChanged.connect(self.e_logoChanged)
        self.logo_size.currentIndexChanged.connect(self.e_logoChanged)
        self.logo_x_slider.valueChanged.connect(self.e_logoChanged)
        self.logo_y_slider.valueChanged.connect(self.e_logoChanged)

        self.caption_group.clicked.connect(self.e_captionChanged)
        self.caption_input.textChanged.connect(self.e_captionChanged)
        self.caption_size.currentIndexChanged.connect(self.e_captionChanged)
        self.caption_color.clicked.connect(self.e_cationColor)
        self.caption_x_slider.valueChanged.connect(self.e_captionChanged)
        self.caption_y_slider.valueChanged.connect(self.e_captionChanged)

        self.camcording_group.clicked.connect(self.e_camcordingChanged)
        self.camcording_path_button.clicked.connect(self.e_camcording_btn_clicked)
        self.camcording_reset_button.clicked.connect(self.e_camcording_reset_btn_clicked)

        self.camcording_path.textChanged.connect(self.e_camcordingChanged)
        self.camcording_slider.valueChanged.connect(self.e_camcordingChanged)

        self.border_group.clicked.connect(self.e_borderChanged)
        self.border_w_slider.valueChanged.connect(self.e_borderChanged)
        self.border_h_slider.valueChanged.connect(self.e_borderChanged)

        self.crop_group.clicked.connect(self.e_cropChanged)
        self.crop_slider.valueChanged.connect(self.e_cropChanged)

        self.resolution_group.clicked.connect(self.e_resolutionChanged)
        self.resolution_ratio.clicked.connect(self.e_resolutionChanged)
        self.resolution_ratio_combobox.currentIndexChanged.connect(self.e_resolutionChanged)
        self.resolution_preset.clicked.connect(self.e_resolutionChanged)
        self.resolution_preset_combobox.currentIndexChanged.connect(self.e_resolutionChanged)
        self.resolution_value.clicked.connect(self.e_resolutionChanged)
        self.resolution_value_w.textChanged.connect(self.e_resolutionChanged)
        self.resolution_value_h.textChanged.connect(self.e_resolutionChanged)

    def center(self):
        frame_info = self.frameGeometry()
        display_center = QDesktopWidget().availableGeometry().center()
        frame_info.moveCenter(display_center)
        self.move(frame_info.topLeft())

    def table_add_row(self, path):
        name = os.path.basename(path)
        i_name = QTableWidgetItem(name)
        i_name.setToolTip(path)
        i_name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        i_name.setTextAlignment(Qt.AlignCenter)

        i_path = QTableWidgetItem(path)
        i_path.setToolTip(path)
        i_path.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        i_path.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount() - 1, 0, i_name)
        self.table.setItem(self.table.rowCount() - 1, 1, i_path)

    def table_highlight(self, idx):
        self.table.item(idx, 0).setFont(FONT_BOLD)
        self.table.item(idx, 0).setBackground(COLOR_GREEN)
        self.table.item(idx, 1).setFont(FONT_BOLD)
        self.table.item(idx, 1).setBackground(COLOR_GREEN)

    def table_unhighlight(self, idx):
        self.table.item(idx, 0).setFont(FONT_BASIC)
        self.table.item(idx, 0).setBackground(COLOR_WHITE)
        self.table.item(idx, 1).setFont(FONT_BASIC)
        self.table.item(idx, 1).setBackground(COLOR_WHITE)

    def viewer_show_preview(self, im):
        pixmap = ImageHelper.to_pixmap(im)
        self.canvas.loadPixmap(pixmap)

    def viewer_show_info(self, meta):
        self.info_name.setText(os.path.basename(meta['path']))
        self.info_path.setText(meta['path'])

        duration = f'{meta["duration"]} sec' if meta.get('duration') else 'None'
        self.info_duration.setText(duration)

        fps = f'{meta["frame_rate"]} fps' if meta.get('frame_rate') else 'None'
        self.info_fps.setText(fps)

        count = str(meta['frame_count']) if meta.get('frame_count') else 'None'
        self.info_count.setText(count)

        w, h = meta['width'], meta['height']
        self.info_size.setText(f'{w} x {h}')

    def viewer_clear_info(self):
        self.info_name.setText('')
        self.info_path.setText('')
        self.info_duration.setText('')
        self.info_fps.setText('')
        self.info_count.setText('')
        self.info_size.setText('')

    def viewer_clear_preview(self):
        self.canvas.pixmap = QPixmap()
        self.canvas.repaint()

    def control_reset_transform_state(self):
        self.brightness.setCurrentIndex(3)
        self.contrast.setCurrentIndex(1)
        self.flip.setCurrentIndex(0)
        self.rotation.setCurrentIndex(0)
        self.framerate.setCurrentIndex(0)
        self.grayscale.setCurrentIndex(0)

        self.logo_group.setChecked(False)
        self.logo_x_slider.setValue(50)
        self.logo_x_slider_label.setText(f'{0:4} %')
        self.logo_y_slider.setValue(50)
        self.logo_y_slider_label.setText(f'{0:4} %')
        self.logo_size.setCurrentIndex(0)
        self.logo_path.setText(LOGO_DEFAULT)

        self.caption_group.setChecked(False)
        self.caption_size.setCurrentIndex(0)
        self.caption_color.setStyleSheet('QWidget { background-color: %s }' % CAPTION_COLOR_DEFAULT)
        self.caption_input.setText(CAPTION_DEFAULT)
        self.caption_x_slider.setValue(50)
        self.caption_x_slider_label.setText(f'{0:4} %')
        self.caption_y_slider.setValue(75)
        self.caption_y_slider_label.setText(f'{0:4} %')

        self.border_group.setChecked(False)
        self.border_w_slider.setValue(0)
        self.border_w_slider_label.setText(f'{0:4} %')
        self.border_h_slider.setValue(0)
        self.border_h_slider_label.setText(f'{0:4} %')

        self.crop_group.setChecked(False)
        self.crop_slider.setValue(0)
        self.crop_slider_label.setText(f'{0:4} %')

        self.resolution_ratio.setChecked(True)
        self.resolution_ratio_combobox.setCurrentIndex(0)
        self.resolution_group.setChecked(False)

    def check_ffmpeg(self):
        def decode(binary):
            try:
                text = binary.decode()
            except:
                text = binary.decode('cp949')
            return text

        p = subprocess.Popen('ffmpeg -version', stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        err = decode(stderr)
        if p.returncode != 0:
            QMessageBox.critical(self, "Error", err)
            exit(1)

    def closeEvent(self, event):
        self.deleteLater()

    def e_reset_transform(self):
        self.core.clear_transforms()
        self.control_reset_transform_state()
        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    # validate preset file
    def e_load_preset_btn_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load Preset', PRESET_DEFAULT_ROOT, '*.json')
        if path != '':
            self.preset_edit_path.setText(path)

            # preset_file = open(path, "rb")
            # preset = pkl.load(preset_file)
            # preset_file.close()
            preset = json.load(open(path, 'r'))
            if not isinstance(preset, dict) or not preset.get('transform') or not isinstance(preset['transform'], list):
                preset = {'transform': []}
            self.e_reset_transform()

            for p in preset['transform']:
                name = p.get('name')
                param = p.get('param')
                if name == 'brightness':
                    self.brightness.setCurrentText(f"{param['value']:+}")

                elif name == 'contrast':
                    self.contrast.setCurrentText(f"{param['value']:+}")

                elif name == 'flip':
                    self.flip.setCurrentText(param['value'].capitalize())

                elif name == 'rotation':
                    self.rotation.setCurrentText(f"{param['value']}")

                elif name == 'framerate':
                    self.framerate.setCurrentText(f"{param['value']} fps")

                elif name == 'grayscale' and param['value']:
                    self.grayscale.setCurrentText('ON')

                elif name == 'logo' and os.path.exists(param['path']) and param['path'].endswith('.jpg'):
                    # file validation
                    self.logo_group.setChecked(True)
                    self.logo_path.setText(param['path'])
                    self.logo_x_slider.setValue(param['x'])
                    self.logo_y_slider.setValue(param['y'])
                    self.logo_size.setCurrentText(f"{param['size']} %")

                elif name == 'border':
                    self.border_group.setChecked(True)
                    self.border_w_slider.setValue(param['w'])
                    self.border_h_slider.setValue(param['h'])

                elif name == 'crop':
                    self.crop_group.setChecked(True)
                    self.crop_slider.setValue(param['value'])

                elif name == 'resolution':
                    self.resolution_group.setChecked(True)
                    if param['selector'] == 'ratio':
                        self.resolution_ratio.setChecked(True)
                        self.resolution_ratio_combobox.setCurrentText(f"{param['value']:+} %")
                    if param['selector'] == 'preset':
                        self.resolution_preset.setChecked(True)
                        self.resolution_preset_combobox.setCurrentText(param['value'])
                    if param['selector'] == 'value':
                        self.resolution_value.setChecked(True)
                        self.resolution_value_w.setText(f"{param['w']}")
                        self.resolution_value_h.setText(f"{param['h']}")


    def e_save_preset_btn_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save Preset', PRESET_DEFAULT_FILE)
        if path != '':
            self.core.save_transforms(path)
            self.preset_edit_path.setText(path)

    def e_brigtnessChanged(self, value):
        print('[Event - Brightness changed]')
        key = 'brightness'
        self.core.remove_transform(key)
        if self.brightness.currentText() != '0':
            self.core.add_transform({'name': key,
                                     'param': {'value': int(self.brightness.currentText())}})

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_contrastChanged(self, value):
        print('[Event - Contrast changed]')
        key = 'contrast'
        self.core.remove_transform(key)
        if self.contrast.currentText() != '0':
            self.core.add_transform({'name': key,
                                     'param': {'value': int(self.contrast.currentText())}})
        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_flipChanged(self, value):
        print('[Event - Flip changed]')
        key = 'flip'
        self.core.remove_transform(key)
        if self.flip.currentText() != 'None':
            self.core.add_transform({'name': key,
                                     'param': {'value': self.flip.currentText().lower()}})
        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_rotationChanged(self, value):
        print('[Event - Rotation changed]')
        key = 'rotation'
        self.core.remove_transform(key)
        if self.rotation.currentText() != '0':
            self.core.add_transform({'name': key,
                                     'param': {'value': int(self.rotation.currentText())}})
        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_framerateChanged(self, value):
        print('[Event - Frame Rate changed]')
        key = 'framerate'
        self.core.remove_transform(key)
        if self.framerate.currentText() != 'None':
            value = int(self.framerate.currentText().replace(' fps', ''))
            self.core.add_transform({'name': key,
                                     'param': {'value': value}})
        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_grayscaleChanged(self, value):
        print('[Event - Grayscale changed]')
        key = 'grayscale'
        self.core.remove_transform(key)
        if self.grayscale.currentText().lower() != 'off':
            self.core.add_transform({'name': key,
                                     'param': {'value': True}})

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_logoChanged(self, value):
        print('[Event - Logo changed]')
        key = 'logo'
        self.core.remove_transform(key)

        if self.camcording_group.isChecked():
            self.core.remove_transform('camcording')
            self.camcording_group.setChecked(False)

        if self.logo_group.isChecked():
            x = self.logo_x_slider.value()
            y = self.logo_y_slider.value()

            self.core.add_transform({'name': 'logo',
                                     'param': {'path': self.logo_path.text(),
                                               'x': x,
                                               'y': y,
                                               'size': int(self.logo_size.currentText().replace(' %', ''))}})

            self.logo_x_slider_label.setText(f'{x:4} %')
            self.logo_y_slider_label.setText(f'{y:4} %')

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_logo_reset_btn_clicked(self):
        self.logo_path.setText(LOGO_DEFAULT)

    def e_logo_btn_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Logo Image', FILE_DIALOG_ROOT, 'Image Files (*.jpg *.png)')
        if path != '':
            self.logo_path.setText(path)

    def e_captionChanged(self):
        print('[Event - Caption changed]')
        key = 'caption'
        self.core.remove_transform(key)

        if self.caption_group.isChecked():
            text = self.caption_input.text()
            font_path = FONT_DEFAULT
            pt = int(self.caption_size.currentText().replace(' pt', ''))
            font_color = self.caption_color.palette().color(QtGui.QPalette.Background).name()

            x = self.caption_x_slider.value()
            y = self.caption_y_slider.value()

            self.core.add_transform({'name': 'caption',
                                     'param': {'text': text,
                                               'pt': pt,
                                               'font_path': font_path,
                                               'font_color': font_color,
                                               'x': x,
                                               'y': y}})

            self.caption_x_slider_label.setText(f'{x:4} %')
            self.caption_y_slider_label.setText(f'{y:4} %')

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_cationColor(self):
        col = QColorDialog.getColor()

        if col.isValid():
            self.caption_color.setStyleSheet('QWidget { background-color: %s }' % col.name())

            self.e_captionChanged()

    def e_camcordingChanged(self, value):
        print('[Event - camcording changed]')
        key = 'camcording'
        self.core.remove_transform(key)

        if self.logo_group.isChecked():
            self.core.remove_transform('logo')
            self.logo_group.setChecked(False)

        if self.camcording_group.isChecked():
            ratio = self.camcording_slider.value()

            self.core.add_transform({'name': 'camcording',
                                     'param': {'path': self.camcording_path.text(),
                                               'ratio': ratio}})

            self.camcording_slider_label.setText(f'{ratio:4} %')

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_camcording_reset_btn_clicked(self):
        self.camcording_path.setText(CAMCORDING_DEFAULT)

    def e_camcording_btn_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Logo Image', FILE_DIALOG_ROOT, '*.jpg')
        if path != '':
            self.camcording_path.setText(path)

    def e_borderChanged(self, value):
        print('[Event - Border changed]')
        key = 'border'
        self.core.remove_transform(key)

        if self.border_group.isChecked():
            w = self.border_w_slider.value()
            h = self.border_h_slider.value()
            if w + h != 0:
                self.core.add_transform({'name': key,
                                         'param': {'w': w, 'h': h}})
                self.border_w_slider_label.setText(f'{w:4} %')
                self.border_h_slider_label.setText(f'{h:4} %')

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_cropChanged(self, value):
        print('[Event - Crop changed]')
        key = 'crop'
        self.core.remove_transform(key)

        if self.crop_group.isChecked():
            val = self.crop_slider.value()

            if val != 0:
                self.core.add_transform({'name': key,
                                         'param': {'value': val}})
                self.crop_slider_label.setText(f'{val:4} %')

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_resolutionChanged(self, value):
        print('[Event - Resolution changed]')
        key = 'resolution'
        self.core.remove_transform(key)

        if self.resolution_group.isChecked():
            if self.resolution_ratio.isChecked():
                val = int(self.resolution_ratio_combobox.currentText().replace(' %', ''))
                self.core.add_transform({'name': key,
                                         'param': {'selector': 'ratio', 'value': val}})

            if self.resolution_preset.isChecked():
                self.core.add_transform({'name': key,
                                         'param': {'selector': 'preset',
                                                   'value': self.resolution_preset_combobox.currentText()}})

            if self.resolution_value.isChecked():
                w = self.resolution_value_w.text()
                h = self.resolution_value_h.text()

                if w != '0' and h != '0' and w != '' and h != '':
                    self.core.add_transform({'name': key, 'param': {'selector': 'value', 'w': int(w), 'h': int(h)}})

                if w == '' or w == '0':
                    w, _ = self.core.thumbnail.size
                    self.resolution_value_w.setText(str(w))

                if h == '' or h == '0':
                    _, h = self.core.thumbnail.size
                    self.resolution_value_h.setText(str(h))

                # if w == '' or w == '0' or h == '' or h == '0':
                #     w, h = self.core.thumbnail.size
                #     self.resolution_value_w.setText(str(w))
                #     self.resolution_value_h.setText(str(h))
                # else:
                #     self.core.add_transform({'name': key,
                #                              'param': {'selector': 'value', 'w': int(w), 'h': int(h)}})

        tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.viewer_show_preview(tt)

    def e_video_add_btn_clicked(self):
        print('[Event - ADD Btn Clicked]')
        paths, _ = QFileDialog.getOpenFileNames(self, 'Select video', FILE_DIALOG_ROOT, VIDEO_EXTENSION_FILTER)

        for path in paths:
            if path.lower().endswith(VIDEO_EXTENSIONS):
                path = os.path.normcase(path).capitalize()
                result = self.core.add_video(path)
                if result:
                    self.table_add_row(path)

    def e_video_add_all_btn_clicked(self):
        print('[Event - Add All Btn Clicked]')
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", FILE_DIALOG_ROOT)
        if directory != '':
            for r, d, files in os.walk(directory):
                for name in files:
                    if name.lower().endswith(VIDEO_EXTENSIONS):
                        path = os.path.normcase(os.path.join(r, name)).capitalize()
                        result = self.core.add_video(path)
                        if result:
                            self.table_add_row(path)

    def e_video_remove_btn_clicked(self):
        print('[Event - Remove Btn Clicked]')
        r = [index.row() for index in self.table.selectedIndexes()]
        if len(r):
            if self.core.video is not None and self.core.video.path == self.core.videos[r[0]].path:
                self.close_video()
            self.table.removeRow(r[0])
            self.core.remove_video_by_idx(r[0])

    def e_video_clear_btn_clicked(self):
        print('[Event - Clear Btn Clicked]')
        self.close_video()
        self.core.clear_videos()
        self.table.setRowCount(0)

    def e_open_video(self, index):
        print('[Event - Video DoubleClicked]')
        self.close_video()

        r = index.row()
        v = self.core.select_video(r)
        self.table_highlight(r)

        self.run_extract_thumbnail(v)

    def e_apply_btn_clicked(self):
        print('[Event - Apply Btn Clicked]')
        if not len(self.core.transforms):
            QMessageBox.warning(self, 'Message', 'Select transformation', QMessageBox.Ok)
        else:
            path, _ = QFileDialog.getSaveFileName(self,
                                                  'Select Target Path',
                                                  os.path.join(TARGET_DEFAULT_ROOT,
                                                               os.path.basename(self.core.video.path)))
            if path != '':
                self.run_video_transform([self.core.video], os.path.normcase(path).capitalize())

    def e_apply_all_btn_clicked(self):
        print('[Event - Apply All Btn Clicked]')
        if not len(self.core.transforms):
            QMessageBox.warning(self, 'Message', 'Select transformation', QMessageBox.Ok)
        else:
            directory = QFileDialog.getExistingDirectory(self, "Select Target Directory", TARGET_DEFAULT_ROOT)
            if directory != '':
                self.run_video_transform(self.core.videos, os.path.normcase(directory).capitalize())

    def e_make_script_btn_clicked(self):
        print('[Event - Make Script Btn Clicked]')
        if not len(self.core.transforms):
            QMessageBox.warning(self, 'Message', 'Select transformation', QMessageBox.Ok)
        else:
            directory = QFileDialog.getExistingDirectory(self, "Select Target Directory", TARGET_DEFAULT_ROOT)
            if directory != '':
                script = self.make_script(self.core.videos, os.path.normcase(directory).capitalize())
                dlg = ScriptDialog(script, self)
                dlg.exec_()

    def make_script(self, videos, target):
        target = [os.path.join(target, os.path.basename(v.path)) for v in videos]
        format = self.core.get_ffmpeg_transform_command_format()

        lines = []
        for v, t in zip(videos, target):
            lines.append(' '.join(v.fill_out_transform_command_format(t, format)))
        return '\n'.join(lines)

    def close_video(self):
        vid = self.core.video
        if vid is not None:
            idx = self.core.find_video_idx(vid.path)
            self.core.release_video()
            self.core.release_thumbnail()
            self.table_unhighlight(idx)
            self.viewer_clear_info()
            self.viewer_clear_preview()
            self.controls.setEnabled(False)

    def run_extract_thumbnail(self, video):
        def extract_thumb_start():
            print('[Extract Thumbnail] start')
            # show loading

        def extract_thumb_finish(code, status):
            print(f'[Extract Thumbnail] Finish code: {code} status: {status}')
            # close loading
            stdout = qp.readAllStandardOutput()
            # stderr = qp.readAllStandardError()

            if code == 0:
                im = Image.frombytes('RGB', (w, h), stdout, "raw", 'BGR')
                self.controls.setEnabled(True)

            else:
                im = Image.new('RGB', (w, h), color='gray')

            self.core.post_thumbnail(im)
            tt = self.core.apply_thumbnail_transform(CANVAS_WIDTH, CANVAS_HEIGHT)
            self.viewer_show_preview(tt)
            self.viewer_show_info(video.meta)

        def occurred_process_error(error):
            # Error Dialog
            print('[Extract Thumbnail] Occurred Process Error', error,
                  'https://doc.qt.io/qt-5/qprocess.html#ProcessError-enum')

        w, h = ImageHelper.get_maximum_size(video.meta['width'], video.meta['height'], CANVAS_WIDTH, CANVAS_HEIGHT)
        cmd = video.build_ffmpeg_thumbnail_command(w, h)

        qp = QProcess()
        qp.started.connect(extract_thumb_start)
        qp.finished.connect(extract_thumb_finish)
        qp.errorOccurred.connect(occurred_process_error)

        qp.start(cmd[0], cmd[1:])
        qp.waitForFinished(THUMBNAIL_RESPONSE_TIME)  # block main app while subprocess is running
        qp.terminate()
        qp = None

    def run_video_transform(self, videos, target):
        def transform_video_start():
            print('[Video Transform] Start')
            self.progressbar.setRange(0, len(videos))
            self.progressbar.setValue(0)
            self.setEnabled(False)

            task = tasks.peek()
            process.start(task['command'][0], task['command'][1:])

        def transform_video_step(exitCode, exitStatus):

            self.progressbar.setValue(self.progressbar.value() + 1)
            task = tasks.get()

            print(f'[Video Transform] progress {exitCode} {exitStatus} {task}')
            log = bytes(process.readAllStandardOutput()).decode().split('\r\n')
            log += bytes(process.readAllStandardError()).decode().split('\r\n')

            logs[task['src']] = {'command': task['command'], 'log': log}
            if exitCode == 0:
                results['results'].append({'src': task['src'], 'dst': task['dst']})

            new_task = tasks.peek()
            if new_task is not None:
                process.start(new_task['command'][0], new_task['command'][1:])
            else:
                transform_video_finish()

        def transform_video_finish():
            print('[Video Transform] Finish')

            dlg = ResultDialog(results, logs, self)
            dlg.exec_()

            self.setEnabled(True)
            process.deleteLater()

        logs = dict()
        results = dict()
        results['transform'] = self.core.transforms
        results['results'] = list()

        target = [os.path.join(target, os.path.basename(v.path)) for v in videos] if os.path.isdir(target) else [target]

        format = self.core.get_ffmpeg_transform_command_format()
        tasks = pQueue([{'command': v.fill_out_transform_command_format(t, format),
                         'src': v.path,
                         'dst': t} for v, t in zip(videos, target)])

        process = QProcess()
        process.finished.connect(transform_video_step)

        transform_video_start()


class ScriptDialog(QDialog):
    def __init__(self, script, parent=None):
        super(ScriptDialog, self).__init__(parent=parent)
        self.script = script
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Transform Script')
        save_btn = QPushButton('Save')
        self.ok_btn = QPushButton('Close')
        text = QTextEdit()
        text.setPlainText(self.script)
        text.setReadOnly(True)
        self.setMinimumSize(SCRIPT_DIALOG_WIDTH, SCRIPT_DIALOG_HEIGHT)

        layout = QGridLayout()
        layout.addWidget(text, 0, 0, 1, 4)
        layout.addWidget(save_btn, 1, 2, 1, 1)
        layout.addWidget(self.ok_btn, 1, 3, 1, 1)

        self.setLayout(layout)
        save_btn.clicked.connect(self.e_save_script_btn_clicked)
        self.ok_btn.clicked.connect(self.e_close_dialog_btn_clicked)

    def e_save_script_btn_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Select Script Path', SCRIPT_DEFAULT_FILE, f'*.{SCRIPT_EXT}')
        if path != '':
            with open(path, 'w') as f:
                f.write(self.script)

    def e_close_dialog_btn_clicked(self):
        self.close()


class ResultDialog(QDialog):
    def __init__(self, result, log, parent=None):
        super(ResultDialog, self).__init__(parent=parent)
        self.result = result
        self.log = log
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Transformation Result')
        self.setMinimumSize(RESULT_DIALOG_WIDTH, RESULT_DIALOG_HEIGHT)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(self.parse_result())
        save_result_btn = QPushButton('Save Result')
        save_log_btn = QPushButton('Save Log')
        self.ok_btn = QPushButton('Close')

        layout = QGridLayout()
        layout.addWidget(text, 0, 0, 1, 4)
        layout.addWidget(save_result_btn, 1, 1, 1, 1)
        layout.addWidget(save_log_btn, 1, 2, 1, 1)
        layout.addWidget(self.ok_btn, 1, 3, 1, 1)

        self.setLayout(layout)

        save_result_btn.clicked.connect(self.e_save_result_btn_clicked)
        save_log_btn.clicked.connect(self.e_save_log_btn_clicked)
        self.ok_btn.clicked.connect(self.e_close_dialog_btn_clicked)

    def e_save_result_btn_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Select Result File', RESULT_DEFAULT_FILE, '*.json')
        if path != '':
            with open(path, 'w') as f:
                json.dump(self.result, f)

    def e_save_log_btn_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Select Log File', LOG_DEFAULT_FILE, '*.log')
        if path != '':
            with open(path, 'w') as f:
                for src, log in self.log.items():
                    line = [f'[{src}]', f'Command : {" ".join(log["command"])}', 'Log :']
                    line += [f'\t{l}' for l in log['log']]
                    f.write('\n'.join(line))

    def e_close_dialog_btn_clicked(self):
        self.close()

    def parse_result(self):
        videos = set(self.log.keys())
        success = set([r['src'] for r in self.result['results']])
        fail = videos - success
        info = []
        if len(fail):
            info += [f'[Fail - {len(fail)} Video]']
            info += [f'\t{f}' for f in fail]
        if len(success):
            info += ['', f'[Success - {len(success)} Video]']
            info += [f'\t{r["src"]} --> {r["dst"]}' for r in self.result['results']]
        info = '\n'.join(info)

        return info


def main():
    app = QApplication(sys.argv)
    win = VideoEditor()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
