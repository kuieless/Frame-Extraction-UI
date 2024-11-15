# 视频帧提取器 (Video Frame Extractor)

## Introduction
The Video Frame Extractor is a graphical user interface application built with PyQt5 and OpenCV that allows users to extract frames from video files. Users can specify the interval for frame extraction and set the output directory. The application also supports GPU acceleration (to be implemented) for improved performance.

## Features
Select multiple video files for processing
Set frame extraction interval
Specify output directory
Support saving extracted frames in separate folders
Preview extracted frames
Delete unwanted frames

## Installation
Ensure you have Python 3.x installed.
Use the following command to install the required libraries:
bash
pip install PyQt5 opencv-python configparser

## Usage
Launch the application.
In the "Upload and Settings" tab, select video files.
Set the frame interval and output directory.
Click the "Extract Frames" button to start extraction.
In the "Preview and Delete Extracted Frames" tab, view the extracted frames, double-click to preview large images, and click the delete button to remove selected frames.

## Configuration
The application will create a settings.ini file in the current directory to save user settings.

## Notes
Ensure that the video file paths and output directory are valid.
The GPU acceleration feature is not yet implemented.

# 简介 (Introduction)
视频帧提取器是一个基于 PyQt5 和 OpenCV 的图形用户界面应用程序，允许用户从视频文件中提取帧。用户可以选择提取的帧的间隔，并指定输出目录。该应用程序还支持 GPU 加速（待实现）以提高性能。

# 功能 (Features)
选择多个视频文件进行处理
设置帧提取间隔
指定输出目录
支持将提取的帧保存在不同的文件夹中
预览提取的帧
删除不需要的帧

# 安装 (Installation)
确保已安装 Python 3.x。
使用以下命令安装所需的库：
bash
pip install PyQt5 opencv-python

# 使用方法 (Usage)
启动应用程序。
在“上传与设置”标签页中，选择视频文件。
设置帧间隔和输出目录。
点击“提取帧”按钮开始提取。
在“预览与删除提取的帧”标签页中查看提取的帧，可以双击预览大图，点击删除按钮删除选中的帧。

# 配置 (Configuration)
应用程序会在当前目录下创建一个 settings.ini 文件，用于保存用户的设置。

# 注意事项 (Notes)
确保视频文件路径和输出目录有效。
GPU 加速功能尚未实现。
